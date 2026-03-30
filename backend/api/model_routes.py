# backend/api/model_routes.py

import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from sqlalchemy import func as sa_func
from typing import Optional, List

from db.database import get_db
from db.models import ModelRecord, ModelRelation, ExecutionLog
from core.registry import registry
from core.validator import validate_meta_code, validate_model_code
from config import settings


router = APIRouter(prefix="/api/models", tags=["模型管理"])


# ══════════════════════════════════════════════════════════════════
# Schema
# ══════════════════════════════════════════════════════════════════

class ValidateRequest(BaseModel):
    code: str


class UploadModelRequest(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    meta_code: str
    model_code: str


class RelatedModels(BaseModel):
    pre: List[str] = []
    post: List[str] = []
    depends_on: List[str] = []
    conflicts_with: List[str] = []


class UpdateRelationsRequest(BaseModel):
    related_models: RelatedModels


# ══════════════════════════════════════════════════════════════════
# 工具函数
# ══════════════════════════════════════════════════════════════════

def _get_related_models(record: ModelRecord, db: Session) -> dict:
    """查询关系表，返回结构化关系（以 name 为值）"""
    relations = db.query(ModelRelation).filter(
        ModelRelation.from_model_id == record.id
    ).all()

    related = {
        "pre": [],
        "post": [],
        "depends_on": [],
        "conflicts_with": []
    }

    for r in relations:
        target = db.query(ModelRecord).filter(
            ModelRecord.id == r.to_model_id,
            ModelRecord.is_active == True
        ).first()
        if target and r.relation_type in related:
            related[r.relation_type].append(target.name)

    return related


def _model_to_dict(m: ModelRecord, related: dict = None) -> dict:
    return {
        "id": m.id,
        "name": m.name,
        "title": m.title,
        "version": m.version,
        "description": m.description,
        "author": m.author,
        "category": m.category or "未分类",
        "call_count": m.call_count,
        "created_at": str(m.created_at) if m.created_at else None,
        "updated_at": str(m.updated_at) if m.updated_at else None,
        "api_path": f"/api/run/{m.name}",
        "related_models": related or {
            "pre": [],
            "post": [],
            "depends_on": [],
            "conflicts_with": []
        },
    }


# ══════════════════════════════════════════════════════════════════
# ✅ 固定路径接口（必须在 /{name} 之前）
# ══════════════════════════════════════════════════════════════════

@router.get("", summary="获取所有已注册模型列表")
def list_models(
    category: Optional[str] = Query(None),
    keyword: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(ModelRecord).filter(ModelRecord.is_active == True)

    if category:
        query = query.filter(ModelRecord.category == category)

    if keyword:
        query = query.filter(
            (ModelRecord.name.contains(keyword)) |
            (ModelRecord.title.contains(keyword))
        )

    models = query.order_by(ModelRecord.created_at.desc()).all()

    return {
        "success": True,
        "data": [
            _model_to_dict(m, _get_related_models(m, db))
            for m in models
        ],
        "total": len(models)
    }


@router.get("/all-names", summary="获取所有模型名称")
def get_all_model_names(db: Session = Depends(get_db)):
    records = db.query(ModelRecord).filter(
        ModelRecord.is_active == True
    ).all()

    return {
        "success": True,
        "data": [
            {
                "name": r.name,
                "title": r.title,
                "category": r.category
            }
            for r in records
        ]
    }


@router.get("/categories/list", summary="获取所有模型分类")
def list_categories(db: Session = Depends(get_db)):
    rows = (
        db.query(
            ModelRecord.category,
            sa_func.count(ModelRecord.id).label("count")
        )
        .filter(ModelRecord.is_active == True)
        .group_by(ModelRecord.category)
        .all()
    )

    result = [
        {"category": r.category or "未分类", "count": r.count}
        for r in rows
    ]

    return {"success": True, "data": result, "total": len(result)}


@router.get("/stats/overview", summary="模型统计概览")
def model_stats_overview(db: Session = Depends(get_db)):
    total_models = db.query(ModelRecord).filter(
        ModelRecord.is_active == True
    ).count()

    total_categories = (
        db.query(ModelRecord.category)
        .filter(ModelRecord.is_active == True)
        .distinct().count()
    )

    total_calls = db.query(sa_func.sum(ModelRecord.call_count)).scalar() or 0

    top_models = (
        db.query(ModelRecord)
        .filter(ModelRecord.is_active == True)
        .order_by(ModelRecord.call_count.desc())
        .limit(5)
        .all()
    )

    recent_logs = (
        db.query(ExecutionLog)
        .order_by(ExecutionLog.created_at.desc())
        .limit(10)
        .all()
    )

    return {
        "success": True,
        "data": {
            "total_models": total_models,
            "total_categories": total_categories,
            "total_calls": int(total_calls),
            "top_models": [
                {
                    "id": m.id,
                    "name": m.name,
                    "title": m.title,
                    "category": m.category,
                    "call_count": m.call_count,
                }
                for m in top_models
            ],
            "recent_logs": [
                {
                    "model_name": l.model_name,
                    "success": l.success,
                    "execution_time_ms": l.execution_time_ms,
                    "created_at": str(l.created_at),
                }
                for l in recent_logs
            ],
        }
    }


@router.post("/validate", summary="校验 meta.py 代码")
def validate_model(req: ValidateRequest):
    result = validate_meta_code(req.code)
    return {"success": True, "data": result}


@router.post("/upload", summary="上传并发布新模型")
def upload_model(req: UploadModelRequest, db: Session = Depends(get_db)):
    meta_validation = validate_meta_code(req.meta_code)
    if not meta_validation["valid"]:
        raise HTTPException(status_code=400, detail={
            "message": "meta.py 校验失败",
            "errors": meta_validation["errors"]
        })

    model_validation = validate_model_code(req.model_code)
    if not model_validation["valid"]:
        raise HTTPException(status_code=400, detail={
            "message": "model.py 校验失败",
            "errors": model_validation["errors"]
        })

    try:
        ns = {}
        exec(compile(req.meta_code, "<meta>", "exec"), ns)
        meta = ns.get("MODEL_META")
        if not meta or not isinstance(meta, dict):
            raise ValueError("MODEL_META 不是有效字典")
        name = meta.get("name", "").strip()
        if not name:
            raise ValueError("MODEL_META.name 不能为空")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"解析 MODEL_META 失败: {e}")

    model_dir = settings.MODELS_DIR / name
    model_dir.mkdir(parents=True, exist_ok=True)

    try:
        (model_dir / "meta.py").write_text(req.meta_code, encoding="utf-8")
        (model_dir / "model.py").write_text(req.model_code, encoding="utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"写入文件失败: {e}")

    try:
        registry.reload(name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"模型注册失败: {e}")

    try:
        record = db.query(ModelRecord).filter(ModelRecord.name == name).first()

        if record:
            record.title = meta.get("title", name)
            record.version = meta.get("version", "1.0.0")
            record.description = meta.get("description", "")
            record.author = meta.get("author", "")
            record.category = meta.get("category", "未分类")
            record.meta_json = meta
            record.is_active = True
        else:
            record = ModelRecord(
                name=name,
                title=meta.get("title", name),
                version=meta.get("version", "1.0.0"),
                description=meta.get("description", ""),
                author=meta.get("author", ""),
                category=meta.get("category", "未分类"),
                meta_json=meta,
            )
            db.add(record)

        db.commit()
        db.refresh(record)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"数据库写入失败: {e}")

    return {
        "success": True,
        "message": f"模型 '{name}' 已发布",
        "data": {
            "id": record.id,
            "name": name,
            "title": meta.get("title", name),
            "category": meta.get("category", "未分类"),
            "api_path": f"/api/run/{name}",
        }
    }


# ══════════════════════════════════════════════════════════════════
# ✅ 更新模型关系（关系表版本）
# ══════════════════════════════════════════════════════════════════

@router.put("/{name}/relations", summary="更新模型关系")
def update_model_relations(
    name: str,
    req: UpdateRelationsRequest,
    db: Session = Depends(get_db)
):
    record = db.query(ModelRecord).filter(
        ModelRecord.name == name,
        ModelRecord.is_active == True
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="模型不存在")

    # ✅ 删除原有关系
    db.query(ModelRelation).filter(
        ModelRelation.from_model_id == record.id
    ).delete()

    # ✅ 插入新关系
    for relation_type, model_names in req.related_models.model_dump().items():
        for target_name in model_names:
            target = db.query(ModelRecord).filter(
                ModelRecord.name == target_name,
                ModelRecord.is_active == True
            ).first()

            if not target:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail=f"目标模型 '{target_name}' 不存在"
                )

            if target.id == record.id:
                db.rollback()
                raise HTTPException(
                    status_code=400,
                    detail="不能将自身设为关联模型"
                )

            db.add(ModelRelation(
                from_model_id=record.id,
                to_model_id=target.id,
                relation_type=relation_type
            ))

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新失败: {e}")

    return {
        "success": True,
        "message": f"模型 '{name}' 关系已更新",
        "data": _get_related_models(record, db)
    }


@router.delete("/{name}", summary="删除模型")
def delete_model(name: str, db: Session = Depends(get_db)):
    record = db.query(ModelRecord).filter(ModelRecord.name == name).first()

    if not record:
        raise HTTPException(status_code=404, detail=f"模型 '{name}' 不存在")

    record.is_active = False

    try:
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"数据库操作失败: {e}")

    model_dir = settings.MODELS_DIR / name
    if model_dir.exists():
        shutil.rmtree(model_dir)

    registry.reload()

    return {"success": True, "message": f"模型 '{name}' 已删除"}


@router.post("/{name}/reload", summary="热重载指定模型")
def reload_model(name: str):
    entry = registry.get(name)
    if not entry:
        raise HTTPException(status_code=404, detail=f"模型 '{name}' 不存在")

    registry.reload(name)
    return {"success": True, "message": f"模型 '{name}' 已重新加载"}


@router.get("/{name}/logs", summary="获取模型执行日志")
def get_model_logs(name: str, limit: int = 20, db: Session = Depends(get_db)):
    logs = (
        db.query(ExecutionLog)
        .filter(ExecutionLog.model_name == name)
        .order_by(ExecutionLog.created_at.desc())
        .limit(limit)
        .all()
    )

    return {
        "success": True,
        "data": [
            {
                "id": l.id,
                "success": l.success,
                "inputs": l.inputs,
                "outputs": l.outputs,
                "error_msg": l.error_msg,
                "execution_time_ms": l.execution_time_ms,
                "created_at": str(l.created_at),
            }
            for l in logs
        ],
        "total": len(logs)
    }


# ══════════════════════════════════════════════════════════════════
# ✅ 动态路径接口（必须最后）
# ══════════════════════════════════════════════════════════════════

@router.get("/{name}", summary="根据 name 查询模型详情")
def get_model(name: str, db: Session = Depends(get_db)):
    record = db.query(ModelRecord).filter(
        ModelRecord.name == name,
        ModelRecord.is_active == True
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail=f"模型 '{name}' 不存在")

    meta = record.meta_json or {}
    related = _get_related_models(record, db)

    data = _model_to_dict(record, related)
    data["inputs"] = meta.get("inputs", [])
    data["outputs"] = meta.get("outputs", [])
    data["execution"] = meta.get("execution", {})

    return {"success": True, "data": data}
