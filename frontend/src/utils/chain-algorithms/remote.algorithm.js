// utils/chain-algorithms/remote.algorithm.js

/**
 * 成链算法 v2：基于拓扑顺序 + 输入输出兼容性校验
 *
 * 算法流程：
 *  1. 按 edges 对分类做拓扑排序，确定执行顺序
 *  2. 对排序后的分类做笛卡尔积，枚举所有组合
 *  3. 对每条组合，逐段校验相邻模型的 outputs → inputs 兼容性
 *  4. 只保留全段兼容的组合
 *
 * @param {Object} ctx
 * @param {Array}  ctx.nodes            - 节点列表（含 key/category/label 等）
 * @param {Object} ctx.candidateModels  - 按 category key 分组的模型列表
 * @param {Array}  ctx.edges            - 分类间的有向边 [fromKey, toKey][]
 * @returns {Promise<Array<{ steps: Array, valid: boolean }>>}
 */
export async function remoteAlgorithm({ nodes, candidateModels, edges = [], multiSelectKeys = ['损失模型'] }) {
  console.log('🔬 remoteAlgorithm v3 执行, 节点数:', nodes.length)

  const validNodes = nodes.filter(
    n => Array.isArray(candidateModels[n.key]) && candidateModels[n.key].length > 0
  )
  if (validNodes.length === 0) return []

  const validKeys = new Set(validNodes.map(n => n.key))

  // ── 拓扑排序（同 v2）──────────────────────────────────────────
  const activeEdges = edges.filter(
    ([from, to]) => validKeys.has(from) && validKeys.has(to)
  )
  const inDegree = {}
  const adjList  = {}
  validNodes.forEach(n => { inDegree[n.key] = 0; adjList[n.key] = [] })
  activeEdges.forEach(([from, to]) => {
    adjList[from].push(to)
    inDegree[to] = (inDegree[to] || 0) + 1
  })
  const queue     = validNodes.filter(n => inDegree[n.key] === 0).map(n => n.key)
  const topoOrder = []
  const visited   = new Set()
  while (queue.length > 0) {
    const cur = queue.shift()
    if (visited.has(cur)) continue
    visited.add(cur)
    topoOrder.push(cur)
    ;(adjList[cur] || []).forEach(next => {
      inDegree[next]--
      if (inDegree[next] === 0) queue.push(next)
    })
  }
  const sortedKeys   = topoOrder.length === validNodes.length
    ? topoOrder
    : validNodes.map(n => n.key)
  const keyToNode    = Object.fromEntries(validNodes.map(n => [n.key, n]))
  const orderedNodes = sortedKeys.map(k => keyToNode[k])

  console.log('📐 拓扑排序结果:', sortedKeys)

  // ── 拆分：互斥节点 vs 多选节点 ────────────────────────────────
  const multiSet      = new Set(multiSelectKeys)
  const exclusiveNodes = orderedNodes.filter(n => !multiSet.has(n.key))
  const multiNodes     = orderedNodes.filter(n =>  multiSet.has(n.key))

  // 多选节点：直接取该分类下所有模型作为"已选集合"（全部叠加）
  const multiSelected = Object.fromEntries(
    multiNodes.map(n => [n.key, candidateModels[n.key]])
  )

  // ── 笛卡尔积（只对互斥节点）──────────────────────────────────
  const pools = exclusiveNodes.map(n => candidateModels[n.key])
  const combinations = pools.reduce(
    (acc, cur) => acc.flatMap(a => cur.map(c => [...a, c])),
    [[]]
  )
  console.log('🎲 互斥节点笛卡尔积组合数:', combinations.length)

  // ── 兼容性校验（同 v2）───────────────────────────────────────
  const edgeSet = new Set(activeEdges.map(([f, t]) => `${f}→${t}`))

  function isCompatible(fromModel, toModel, fromKey, toKey) {
    if (!edgeSet.has(`${fromKey}→${toKey}`)) return true
    const outputNames = new Set(
      (fromModel.outputs || []).map(o => typeof o === 'string' ? o : o.name)
    )
    const requiredInputs = (toModel.inputs || []).filter(
      i => typeof i === 'object' && i.required !== false
    )
    if (requiredInputs.length === 0) return true
    return requiredInputs.every(i => outputNames.has(
      typeof i === 'string' ? i : i.name
    ))
  }

  const validCombinations = []
  let skipped = 0

  for (const combo of combinations) {
    let chainValid = true
    for (let i = 0; i < exclusiveNodes.length - 1; i++) {
      const fromKey   = exclusiveNodes[i].key
      const toKey     = exclusiveNodes[i + 1].key
      if (!isCompatible(combo[i], combo[i + 1], fromKey, toKey)) {
        chainValid = false
        break
      }
    }
    if (!chainValid) { skipped++; continue }

    // 组装 steps：互斥节点每个选一个，多选节点附加完整列表
    const exclusiveSteps = exclusiveNodes.map((node, idx) => ({
      nodeKey:  node.key,
      labelCN:  node.labelCN,
      label:    node.label,
      icon:     node.icon,
      category: node.category,
      model:    combo[idx],          // 单个模型
      multi:    false,
    }))

    const multiSteps = multiNodes.map(node => ({
      nodeKey:  node.key,
      labelCN:  node.labelCN,
      label:    node.label,
      icon:     node.icon,
      category: node.category,
      models:   multiSelected[node.key],  // 模型数组（全部叠加）
      multi:    true,
    }))

    // 按拓扑顺序合并两类 steps
    const allSteps = orderedNodes.map(node => {
      if (multiSet.has(node.key)) {
        return multiSteps.find(s => s.nodeKey === node.key)
      } else {
        return exclusiveSteps.find(s => s.nodeKey === node.key)
      }
    })

    validCombinations.push({ steps: allSteps })
  }

  console.log(`✅ 有效组合: ${validCombinations.length}, 过滤掉: ${skipped}`)
  return validCombinations
}

