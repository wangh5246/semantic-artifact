# 向量承诺替代路线的接口与验收门

状态：vector 版本化关系已实现（保留 state 状态/策略/身份，移除 masked-moment）；N=8 功能与 proof 门通过，D=10001 资产/计时与真实 retained 字节检查在执行中。完整 live Janus 接线、authority 证明验证、逐报告份额和隐私/侧信道论证仍未完成。此路线是基于 Prio3 Histogram 的新适配设计，不称为对某篇已有协议的原样复现。

## 共同语义

沿用当前 state 的身份、隐藏 genesis、前驱/锚点、配额、注册、完整 P/R 锁定和首次暴露 reservation；Prio3 的 task、report、HPKE 和 role 保持同源绑定。接受的正贡献由 `p=100*cell_y+cell_x` 决定；零贡献使用 10000 sentinel。每个角色的承诺覆盖其**实际保留**的 10001 个规范 Field128 元素、role、固定 report context 与私有随机盲量。

证明关系必须同时约束：state hidden state 当前格和贡献位、两个份额向量及其上下文承诺、每个坐标按 Prio3 field 加法重构为对应 one-hot（包括 sentinel）。单独证明两个关联的 commitment、仅在证明中接收客户端给出的份额，或只检查加密报文字节摘要，都不足以连接接收端实际 output。

## 需要实现的版本化接口

1. **关系与资产。** 新 relation ID、公共信号顺序、对双方 share 的绑定承诺及证明；proof 的 `p` 与现有 ADWC witness 使用同一约束变量，`bit=0` 仍要保持 ADWC 关系与实际 head/anchor 检查。以新资源目录生成 witness、研发 setup、proving 与verification assets，保留原电路和原keys。
2. **客户端。** 从 Prio3 原生 shard 按当前版本提取两个 measurement share，按照相同规范编码形成承诺及证明，并使用新版本 sidecar 分别加密盲量。上下文包含 task、report ID、版本、role、window、语句及关联信息。具体序列化必须解除自引用，不能将尚未计算的 ciphertext/body digest 循环放入承诺。
3. **两个receiver。** 在真实保留 output 的 receipt 路径，读取该角色 `retained.aggregate_share`，规范解码、使用本角色盲量和正确context重算承诺，签名的receipt绑定真实 native session 和承诺。blind/opening 不发给另一角色或authority。拒绝非规范、错 role、错 context、错 blind、错份额及跨 report replay。
4. **authority/commit。** 验证新proof并把其公共同一承诺与两份角色签名receipt核对；保持 P/R、当前head、配额、CAS、完整冻结/首次暴露路径。不同 statement/version 不得跨用已有验证键或receipt。
5. **保密及时序。** 现有 JavaScript/WASM 参考适配器不具备生产恒定时间或安全隔离保证。实际receiver需要适合秘密值的实现、随机盲量、相关泄漏论证与错误反馈分析；不能把合成负控视作隐私证明。Poseidon 承诺的 binding/hiding 假设和域分离也需明确。

## 递进验收

先对小维度单报告实际 proof/verifier 与真实receiver路径执行clean、wrong-cell、两种role替换、跨report/context、零贡献和缺成员等正负控。复核本地与receiver处理的实际bytes、proof statement、ADWC current head、两receipt与已保留output的一致性及首曝前完整集合。所有失败保留，任何缺失的连接为未通过。

达到该门后，在 D=10001、同一 trace/机器/并发/registration/lock/endpoint 下，独立版本登记并分别运行替代与 masked-moment，记录 witness/prove、接收端验证/处理、authority/native/DB CPU、传输字节和包含范围清楚的wall；每个条件报告实际样本数、配对值和变异。若不能完成大维度setup/proving，报告资源阻塞或子关系结果，不能用估计数替代测量，也不改变之前停止的Full-r2。

## 已有具体证据

- 8-bin电路5900个实际R1CS约束，合成正例及负控14项；已有Prio3原生Shard生成的两组合成份额亦14项。文件和回执见 `../../outputs/matched-vector-binding-20261028/`。
- 离线参考adapter从两组规范合成份额字节重算承诺，与电路witness的公开承诺一致；22项检查。它还没有接入真实receiver，不是可信的生产密码学实现。
- prio 0.16.8 `prepare_next` 从measurement share得到output share，Histogram `truncate`在长度检查后原样返回。接收端源码中 receipt 使用 `retained.aggregate_share`。这是可供后续精确接线的源码对应，尚需证明具体二进制、字段编码与改造后的调用链一致。

## vector 实现状态（2026-10-28）

- 关系 `Alternative(N)`：保留 state 三元组状态承诺/策略、payload、ticket 与身份/上下文；去掉 mask 承诺与 `masked_native_index`；新增两角色向量承诺 `cv_r = Poseidon(2N+r, blind_r, ctx, share_r)`、逐坐标 `s0[i]+s1[i]=onehot_i+carry_i·Q`、sentinel `N-1`，以及 `rcpt_r=Poseidon(Poseidon(r,cv_r,ctx),rid,bit,ρ_r)`。公共信号 22 个，`relation_version=6`。
- `N=8`：10,530 约束；13 项组合 witness 正负控通过；Groth16（pot14，与 state 同 ceremony）setup 36.71 s、prove 2.52–2.55 s、verify 0.022 s、723 B。`N=10001`：851,715 约束；编译通过；zkey/prove 与真实 retained 字节检查在执行中。
- canonical 份额边界：电路不做 128-bit range check；接收端先将 retained 字节解码为规范 Field128（拒绝 ≥Q），承诺绑定使证明中的份额必须等于该规范值。该边界由 `noncanonical-share-circuit`（电路接受）与接收端解码拒绝两项分别记录。
- 真实 retained 检查：对 T-Drive、Porto clean 运行导出的 160,016 B/角色 aggregate payload 完成规范解码、承诺确定性重算、字节翻转/错 role/错 context 负控；重建 8 个非零格、质量 8。它是导出的**聚合** payload（8 条报告之和），不是逐报告份额；逐报告 one-hot 关系由合成 fixture 证明。
- 仍未实现：live Janus receiver 调用链、authority 端证明验证、逐报告 retained 份额、隐私/侧信道/恒定时间论证、D=10001 的最终计时（运行中）。
