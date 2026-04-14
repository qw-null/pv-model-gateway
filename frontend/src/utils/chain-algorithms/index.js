// utils/chain-algorithms/index.js

export { cartesianAlgorithm } from './cartesian.algorithm.js'
export { remoteAlgorithm }    from './remote.algorithm.js'
export { ruleBasedAlgorithm } from './rule-based.algorithm.js'

/**
 * @typedef {Object} ChainContext
 * @property {Array<{ key: string, label: string, labelCN: string, category: string, icon: string }>} nodes
 * @property {Record<string, any[]>} candidateModels
 */

/**
 * @typedef {Object} ChainStep
 * @property {string}  nodeKey
 * @property {string}  labelCN
 * @property {string}  label
 * @property {string}  icon
 * @property {string}  category
 * @property {any}     model
 */

/**
 * @typedef {Object} ChainResult
 * @property {ChainStep[]} steps
 */

/**
 * 同步算法签名
 * @callback ChainAlgorithm
 * @param {ChainContext} ctx
 * @returns {ChainResult[]}
 */

/**
 * 异步算法签名（用于远程拉取数据的算法）
 * @callback AsyncChainAlgorithm
 * @param {ChainContext} ctx
 * @returns {Promise<ChainResult[]>}
 */
