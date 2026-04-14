// chain-algorithms/cartesian.algorithm.js

/**
 * 默认算法：自动枚举所有节点候选模型的笛卡尔积组合
 *
 * @param {{ nodes: Array, candidateModels: Record<string, any[]> }} ctx
 * @returns {Array<{ steps: Array<{ nodeKey: string, model: any }> }>}
 */
export function cartesianAlgorithm({ nodes, candidateModels }) {
  // 只保留有候选模型的节点
  const validNodes = nodes.filter(
    n => Array.isArray(candidateModels[n.key]) && candidateModels[n.key].length > 0
  )

  if (validNodes.length === 0) return []

  const pools = validNodes.map(n => candidateModels[n.key])

  // 笛卡尔积
  const combinations = pools.reduce(
    (acc, cur) => acc.flatMap(a => cur.map(c => [...a, c])),
    [[]]
  )

  return combinations.map(combo => ({
    steps: validNodes.map((node, idx) => ({
      nodeKey: node.key,
      model:   combo[idx],
    })),
  }))
}
