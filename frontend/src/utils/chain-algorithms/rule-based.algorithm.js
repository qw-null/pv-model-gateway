// utils/chain-algorithms/rule-based.algorithm.js

import { cartesianAlgorithm } from './cartesian.algorithm.js'

/**
 * 预留：基于规则的成链算法
 * 后续在此实现：输入输出变量匹配、上下游接口兼容性校验、非法链剪枝等
 *
 * @param {{ nodes: Array, candidateModels: Record<string, any[]> }} ctx
 * @returns {Promise<Array<{ steps: Array<{ nodeKey: string, model: any }> }>>}
 */
export async function ruleBasedAlgorithm({ nodes, candidateModels }) {
  // TODO: 替换为真实成链算法
  // 目前直接透传给 cartesianAlgorithm 兜底
  return cartesianAlgorithm({ nodes, candidateModels })
}
