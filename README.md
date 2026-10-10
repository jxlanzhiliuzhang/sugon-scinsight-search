# sugon-scinsight-skill

`sugon-scinsight-skill` 是一个基于 MCP 的科学文献检索 Connector，用于查论文、找文献、搜索相关研究和文献调研。

## 核心能力

Connector 的首选工具是 `searchAcademicLiterature`。它根据用户原始问题，对运行时已配置并启用的学术数据源进行检索、聚合，并返回结构化文献元数据。

默认数据源包括：

- Crossref
- Semantic Scholar
- OpenAlex
- arXiv

实际启用的数据源以部署配置为准。以上数据源是底层聚合来源，不代表 Connector 暴露了对应的独立工具。

## MCP 配置

- 服务地址：`https://sci.ksai.scnet.cn:58043/scnetmcp`
- 传输方式：Streamable HTTP
- 请求超时：360000 毫秒

## 使用约定

- 学术检索请求优先调用 `searchAcademicLiterature`。
- `query` 必须原样传递用户的问题，不得自动翻译、改写或生成替代查询。
- `query` 最大长度为 128 个字符。
- `topN` 最大为 50；用户未指定数量时，调用方推荐显式传入 `topN=10`。
- 检索结果必须以 `📚 检索来源:科学文献洞察智能体-文献检索` 开头。
- 只能展示工具实际返回的文献，不能补造标题、作者、DOI、摘要、引用数量或 URL。
- 工具错误、空结果和成功结果必须明确区分。

完整的调用、参数、展示和错误处理规则见 [SKILL.md](SKILL.md)。

## 版本

当前版本：`2.1.0`