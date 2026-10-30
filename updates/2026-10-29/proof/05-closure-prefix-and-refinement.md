# G4b：声明闭合、全前缀与实际源码的精化对应

日期：2026-10-18。对象为冻结的 `SHTPC-native-hidden-adwc-strict/v5` G4a 加固实例，实际源码仍是 `authority_v5_g4a`、`janus-v5-g4a`；本轮不改源码、资产、G4a证明或历史证据。本文给出参数化状态机归纳、逐操作的手工前向精化和源码对应；有限脚本只核对对应路径、哈希和小模型，不是自动验证编译器或完整G5。

## 1. 定理对象、参数与执行前提

固定task、事前生成的verification key、profile/config/asset身份、TimeInterval、NoDifferentialPrivacy、两方单proof的 `Prio3Histogram(10001,100)`，native field为q。按task唯一dispatch pin，本实例至多一个visible cohort。其他窗口可以构成声明历史，不能据此主张它们也能发布。G4a的模型 [source omitted from this derivative]、04 [source omitted from this derivative]、05 [source omitted from this derivative]、执行层 [source omitted from this derivative]和组合 [source omitted from this derivative]为冻结实例入口。

完整性实验C要求authority、两roles、Finalizer/Decoder正确，原生verification key在正确setup中随机采样且对恶意客户端隐藏。隐私实验P/P+A允许一role主动恶意并知道该原生key，仍要求诚实role的本地集合、留存和发出路径遵守本文；不能把C中两role正确且query不可预知的native validity或moment结论转移为P中的恶意输出正确性。authority单独实验A没有aggregate oracle。

执行前提是：诚实完整SignedBody在既有登记边界前经独立认证保密路径持久交付；client在input-ready之前完成witness/prove并按预定计划投递；正确持久存储和数据库原子提交/恢复；不回滚已提交状态，不泄漏诚实密钥。消息延迟、丢失、重复、进程crash可以任意发生。这里没有假定所有业务终会成功，没有将真实时间、timeout或秘密verdict加入metadata。

PostgreSQL源码实际用 `REPEATABLE READ`，不是全库SERIALIZABLE。下文只对相关操作证明所需的线性化/单调读性质。所谓正确数据库不包括“忽略冲突照常提交”或损坏已保留字段；这些是执行前提，不是可忽略坏事件。

## 2. 抽象状态及精化关系

对每个窗口，P为锁定的完整 `LockedRecord` 有序映射，R=eligible(P)，L为authority真实commit记录映射，A=eligible(L)。对role s，L_s为本地已经接受的同一CommitCert记录，M_s为实际并入native batch的eligible记录映射。不能把锁P、实际L、eligible A、实际M的集合身份混用。

状态还含：每uid实际head/version/history、每uid/window quota、Origin表、不可变body/slot/RID、install/permit、受保护输入身份与journal、retained output、outbox、freeze/abort、reservation E_s、唯一payload Z_s和暴露账本X。retained的联系为

`(task,profile,config,body,RID,job,protected-step,request-hash,aggregation-param,role) → typed output + opaque retained tag`。

完整锁记录不含未来尚未产生的session/output。后者由receipt、CommitCert、本地retained和reservation附加绑定，不能在锁后偷偷修改P。M中的每条记录必须带这条实际关联；只比较RID/count/checksum不能代替记录相等。

前向关系α把SQLite/Pg**已提交**行投影到上述状态。authority `bodies.committed/commits/history/quota/identities`决定L/head；role `commit/head/history`决定L_s；eligible retained APPLIED加consumed membership及实际batch决定M_s；warmup虽可被标APPLIED，仍不加入M。未提交事务、线程栈、等待锁、network buffering不直接增加这些集合。journal/immutable bytes的读取是stutter，获准第一次写是相应抽象事件。

X记录已发生的语义暴露，首次诚实share离开受信role交给具有解密能力的接收方时追加。实现可能只记录保守的send intent：这允许误报“可能已暴露”，不能漏报或用未知状态证明零暴露。reservation持久而尚未发送不必等同实际交付；理想证明允许在准备首次发送时提前取得一次相同R的输出，未使用的查询不交给敌手，不能借此查询其他集合。

## 3. 线性化与crash边界

| 操作族 | 线性化点及实际机制 | 可见返回之前的义务 |
| --- | --- | --- |
| authority origin/register/lock/permit/receipt/freeze/abort | `service._transaction`的SQLite COMMIT；`guard`加 `BEGIN IMMEDIATE`串行写 | result只在COMMIT成功后返回；异常ROLLBACK。proof verification可在最终register事务外，但attempt先持久预留，最终事务重验slot/origin/lock不可变条件 |
| authority→role发送 | `_proxy_queue`提交exact request，`_proxy_deliver`提交attempt后才网络发送；回复、ack是后续事务 | authority commit与两role apply不构成跨库原子事务；commit证书持久可恢复，驱动器从commit表重新补投。不能假称所有outbox行与authority commit同一事务写成 |
| role control与Helper init/continue | `Datastore::run_tx`最终Pg commit；control advisory lock与prepare lock按固定顺序，共享 `prepare_serialization` epoch写 | REPEATABLE READ等待者的旧snapshot在epoch冲突处重试，发生在authorization/私密prepare之前；journal、native状态、retained和响应同事务。失败尝试不能将临时response发送 |
| Leader native任务 | unit aggregation parameter下，report的`aggregation_started`置位、job/report-state创建和原report scrub同事务；每步读取已提交state后可在事务外计算 | `step_aggregation_job_2`把writer/retained写入与`release_aggregation_job`同事务提交；后者按lease expiry/token匹配，失去lease的结果使全事务失败，不能覆盖新的已提交分支 |
| role apply | control/epoch事务内merge batch、consumed membership、head/quota/history、retained/body状态及commit行一并提交 | commit已存在则exact证书返回缓存；不同证书拒绝；并入一次，不以网络ack作为第二次merge条件 |
| role reserve/bind | control锁内检查完整P/R/retained/M并唯一写reservation；bind再次reserve、写固定160016B BYTEA并全长CT比较，所在Pg commit后才返回 | Helper fresh/cache与Leader finished/cache各在HPKE前await bind事务；Leader在请求Helper前也先完整reserve |
| freeze/abort/失败结果 | authority freeze在完整L=P且无active permit时提交；role按真实本地L/M检查；abort不删已commit行 | FREEZE不可与同锁新的合法ABORT/commit并存；`proxy_abort`未知状态标UNKNOWN，曾可能发送则永久保持exposed类别 |

Helper的HADWC journal固定一个**已提交的受保护输入分支与响应**，变化请求在私密处理前冲突。Leader没有相同的first-peer-input日志；它依靠上述持久job/state和lease fence，每步只提交一个transition。其首次发往Helper的prepare message由固定已存report/nonce/key决定，可以在本步状态提交前发送；这不是aggregate首曝。若计算后crash、lease被重新取得或提交失败，重试可以收到不同Helper响应并重新计算。它仍使用同一原始share、nonce/query/joint coins及已提交native状态；03的同一`Σ,z_h`可计算每次变化peer输入的真实谓词，不能把这些计算假称必在处理前拒绝。只有本步成功写入的state/retained成为α中的转换，旧lease的写入整体回滚；正确Helper则对该请求始终给同一持久response。

Pg `run_tx`也可能因serialization/deadlock重新调用closure。这些机制保证一个**已提交的逻辑分支**，不是“CPU永不重复执行任何指令”。同输入重算复用同RO流；变化peer响应的未提交重算也须按03模拟，物理调用、失败、消息和时序全部计入Q/T。独立本地coins由执行层模拟，不能从预算删除。

export reserve没有单独写prepare epoch；不能从advisory lock声称它一定读取最新snapshot。其安全来自单调阶段：看不到freeze或完整M的旧snapshot只会拒绝；能看见正确freeze时，authority已终结完整P，此后不能合法ABORT/新commit。role的L/M只能从子集增至固定P/R，不可删除、更换retained或回滚。读到fullP/R+APPLIED因而是永久稳定事实；唯一reservation/payload冲突由写约束、全记录/全长比较和Pg提交处理。如此所需读断言稳定，无需把REPEATABLE READ升级成不存在的隔离级别。

crash在事务内对应未提交/回滚或已提交二者之一；aggregate/receipt及Helper缓存response在相应提交之后发送。Leader提交前的固定报告prepare消息与未提交反馈按上段处理。已提交后发送前crash只重用同对象；发送后丢reply并不取消敌手观察。双库交付通过幂等cert和角色各自的任务恢复，不要求跨机器原子commit。故障损坏持久库或管理员回退不在这个crash模型中。

## 4. 全前缀不变式

对任意有限prefix τ，以下同时成立；“相等”均为完整类型记录及关联相等：

1. P/R、task/profile/config/assets、聚合参数与selector锁后固定，R=eligible(P)；每origin、slot、RID和body首次写定后不换身份。
2. L⊆P，真实history依赖闭合；每uid head是已commit唯一链的末端，K为实际 `max(0,t−6)`，version随一次commit递增，quota恰为已commit计数，无回退。
3. L_s⊆L；M_s⊆eligible(L_s)，且每成员恰有一个正确retained/body/session/link并且实际batch包含其输出一次。warmup不在M，eligible b=0在M。
4. Helper每个journal key只含一个已提交first-input/result/native-state/response，report tombstone禁止换job打开第二分支；其exact retry返回同wire，变化只得到公开冲突。Leader同报告唯一持久job、逐步state及lease fence保证每步仅一个已提交transition；提交前可变peer响应重算不扩大已提交状态，其全部反馈由同一模拟verifier产生。
5. E_s存在则L_s=P、eligible(L_s)=R、M_s=R，完整ordered records、retained links、selector、snapshot身份固定。bound payload为 `Z_s=Σ_(i∈R)v_(s,i)` 的真实native编码，之后不能替换。
6. 每个可解密诚实aggregate share发送前已有持久E_s和bound Z_s。外层HPKE可重随机，同payload只是一项语义输出；失败、abort或重启不撤回X。

对预锁阶段，用可增registered图P_reg表达；锁事件一次把完整P_reg固化为P。其余事件不得悄悄重定义“完整”所指的对象。

## 5. 逐事件归纳证明

**初始/enrollment/origin。** 配置/角色/owner固定，合法genesis由适用的提取及规范STATE编码确定。history仅genesis，quota零。origin唯一索引预占未来RID但不推进head。无L/M/journal/export，六项成立。

**register。** 来源/owner/rawRID与证书检查、proof验证、完整规范record生成后，最终事务核未过登记边界/未锁、slot/RID唯一且origin等于预留值。它只增加P_reg、PendingCert和业务记录，不改L/head/quota/M。失败attempt计数可增长但不产生接纳历史。并发body仅唯一约束允许一个；hash无碰撞前同id代表同字节。

**lock。** 事务要求预定slot集合全部存在、每候选链连续、根连接实际head、所有prev/K引用存在且规范；按完整record排序求P/R root，eligible distinct UID满足公开门槛。一次写P/R/LockCert，后续registration拒绝。没有把任意接收交集当完整集合。它保持历史未推进。

**install/permit。** role验证整包、LockCert、全记录/roots并不可变持久化。authority收到两个install ack后，读取实际head/version、真实已commit prev/K和quota，只签一个active permit。pending后继未变成history。role收到permit再核相同body/record/上下文。异步L_s可以落后L，不能因此放宽导出门。

**prepare/retain。** upload/helper-init/continue在HPKE/FLP前核完整安装包与活动permit。Helper共享epoch在私密处理前排除旧snapshot授权；first job/context/input和已提交response固定。missing journal或changed peer input不能复用其旧success或重开分支。Leader以持久report的单次unit-param job分配固定原始输入，以lease fence提交每步native状态；事务外计算及变化peer响应的重算按§3处理，不能从α反推这些计算未发生。正确Finished输出只隔离留存在retained中，暂不进入M；writer中的retained与本步state/lease释放同事务提交。重复完成的body/job/output必须全部相等；opaque tag沿用原值。由此无第二个已提交branch，物理反馈则由03完整verifier覆盖。

**receipt。** 正确role只从同一retained输出和同body sidecar计算masked moment，固定binary mask/rho解码与CT秘密段见G4a08；签名绑定lock/permit/body/statement/session/nonce/step/tag。第一方receipt持久化不等于commit；冻结后只准exact缓存重放，不签新receipt。错误不改L/M。

**authority commit。** 第二receipt事务核两方签名和全部binders、session、moment，再查真实head/version、真实prev/K digest与quota。CAS、history、quota、permit inactive、body committed与CommitCert同COMMIT生效。失败事务不留下半个history或多扣额度；并发兄弟只能一个从原head成功。由旧history闭合和同commitment唯一opening，新的L仍合法依赖闭合。已经commit的exact replay不再扣quota。

**role commit/apply。** 核authority证书、自己的已存receipt、两个receipt、安装record、retained job/tag，exact旧commit立即幂等返回。对eligible才merge原始retained vector并写consumed membership；warmup只推进本地history。之后的head/version/quota CAS及status/commit也在同一事务；任一失败回滚merge。故M无重加、错包或漏zero，L_s⊆L。此处靠authority签名与诚实role代码，P不要求恶意role也遵守。

**freeze。** authority要求L=P、全records未变且无active permit；签完整p/r列表并把lock置FROZEN。role验证本地完整已commit/apply关系后持久freeze。没有从authority“已commit”推断另一role已经apply；迟到role须先补齐cert，导出仍独立检查本地M。

**reserve/bind/send。** 所有出口重验完整P/R、eligible投影、session/tag及实际consumed集合。insert frozen native membership后还查差集，排除多余成员。唯一E_s完整身份，bind再次检查并固定真实native输出。已有E_s/bytes只能相同。await事务成功后才HPKE和send，故首个share即完整R；native count/checksum/collection失败不能撤回此前E/X。fresh和cache走同门，不存在“缓存默认可信”的豁免。

**abort/timeout/recovery。** 非frozen abort只终结lock/permit，保留commits/head/quota、journal与tombstone；它不能删P/R再继续导出。frozen后的collect失败只保留并重试原snapshot。proxy status丢失给UNKNOWN，已可能暴露不可降为PRE；这些是保守业务标签，精确X由发送事件定义。crash按§3分割事务，恢复读取持久状态，重复消息由以上幂等分支处理。stutter、延迟、读取、外层重加密均不破坏六项。列举覆盖改变集合、head、quota、journal、payload与暴露的全部事件，完成任意prefix归纳。

## 6. 声明闭合与成功重建

排除适用提取失败、正确签名伪造、承诺双开口、SHA绑定碰撞和native validity误接纳等明确坏事件。C中从genesis归纳，规范STATE编码单射且message<ℓ，prev/K相同承诺强制相同规范坐标；坐标差、平方、mask carry等上界都低于SNARK p，不能借域环绕满足错误整数关系。每步因此是该已接纳声明历史的ADWC关系，而非物理位置真实性。

单个完成报告的两正确输出满足 `v_A+v_R=e_y`，0≤y≤D；选中Histogram有效域是一热，不能换SumVec多1/零向量。F(v)=Σkv[k]只在E={e_0,…,e_D}上单射。正确retained receipt与MASK opening给

`F(v_A+v_R)=m_A+m_R−r_A−r_R=T−r_A−r_R=x (mod q)`。

x,y≤D<q，所以y=x。b=0得到真实sentinel e_D，仍有retained与membership。由全前缀定理，成功同selector的两snapshot只加固定完整R，各成员一次，解码删sentinel后恰得 `Σ_(i∈R)b_i e_(j_i)`。C成功正确性是条件命题，不承诺恶意owner缺席或permanent censorship下输出。

上述总和作为整数histogram解读也无native模q环绕：选中的deferred apply每次并入一个report，持久batch的report_count在 `models.rs:1498` 经 `i64::try_from` 编码，超出即失败回滚。前一成功count至多2^63−1，下一次加1仍不溢出u64。全selector可能跨多个batch shard，不能只从每shard的i64界直接推其总数；实际Helper `put_aggregate_share_job`（`datastore.rs:4412`）在发送前、Leader `update_collection_job`（同文件3512）在FINISHED持久化时，都对**总**report_count再作`i64::try_from`。真实003 debug的u64总数加法也不静默环绕。因此成功collect完整R有 `|R|≤2^63−1<q`，每桶计数亦小于q。不把任意大R的F_q和默认等同未约束的整数histogram。若未来换count/持久格式或overflow语义，须重证这个无wrap条件。

P/P+A中非H记录实际输出可以非一热，不继承上述C结论。其模拟aggregate严格用

`O_C(R)−Σ_(i∈R\H)e_(x_i)−Σ_(i∈R∩H)v_(c,i)^orig+Σ_(i∈R\H)w_(h,i)^actual`。

这里非H声明桶由新statement提取/已知witness，实际诚实输出由合法CCA解密后真实native处理；无需腐化role私钥。H原始份额才有互补恒等式。此式只使用获准完整R输出，没有新增子集oracle。

## 7. 源码映射与有限旁证

source-map.json [source omitted from this derivative] 给52个实际函数/出口的repo相对路径、起止行及全文件SHA，脚本同时确认G4a build003全部288 source pins不变。矩阵包括authority事务/注册/锁/permit/commit/freeze/abort、proxy outbox/exposure、Pg事务/epoch、Helper身份/journal、Leader单job分配/事务外compute/lease-fenced提交、retained、receipt/apply/batch merge、reserve/bind、task dispatch、context/record codec与三类真实出口。函数名或hash本身不证明语义；§§3–5是这些行的手工对应理由。check001–004保留历史范围，不被重写。

bounded-controls.json [source omitted from this derivative] 对两条独立eligible记录（一正一zero的成员身份）枚举两个role crash/recovery、prepare/commit/apply/freeze/reserve/bind/send及失败标签。正模型穷尽840状态、2652边，无命名不变式违反，PRE/EXPOSED/EXPOSED_FAILED均可达；8个移除守卫变体各有预期最短trace。模型的prepare事件是**已提交**transition，no-journal变体表示删除该提交唯一性（Helper日志或Leader fence），不是宣称所有物理peer输入唯一。它不计算真实proof/FLP、不证明任意规模head/K链、不等同TLC，也不冒充G5/native故障campaign。

当日G5 E5/1是单独旁证，其L变量为 `lockLog`（锁定P），而本文L为实际committed；翻译需 `G5.lockLog→P`、`G5.committed→L`、`EligibleIn(committed)→A`、`merged[s]→M_s`。G5用单slot captured share和只能由mutant设置的dup/redo/badOutput flags抽象关键义务，且只有限candidate集合；它的35用例、模型PASS不构成本源码的无界精化定理。本文不修改或并入其冻结manifest，不把G5尚未验收的native crash/race记为通过。适用范围及守卫反例详见[06](06-counterexamples-and-scope.md)。


### 7.1 实际函数/行/SHA对应矩阵

SHA列为便于核对的前12位，完整64位与repo-relative路径均在上面的JSON；同文件不同函数共享文件SHA。

| 对应事件/义务 | 实际源文件及行 | SHA256前12位 |
| --- | --- | --- |
| authority-tx | runtime/authority_v5_g4a/service.py [source omitted from this derivative]：184–191 | `ced8a6fd317b` |
| origin | runtime/authority_v5_g4a/service.py [source omitted from this derivative]：239–259 | `ced8a6fd317b` |
| register | runtime/authority_v5_g4a/service.py [source omitted from this derivative]：274–321 | `ced8a6fd317b` |
| lock | runtime/authority_v5_g4a/service.py [source omitted from this derivative]：323–346 | `ced8a6fd317b` |
| permit | runtime/authority_v5_g4a/service.py [source omitted from this derivative]：375–399 | `ced8a6fd317b` |
| authority-commit | runtime/authority_v5_g4a/service.py [source omitted from this derivative]：400–444 | `ced8a6fd317b` |
| authority-freeze | runtime/authority_v5_g4a/service.py [source omitted from this derivative]：446–474 | `ced8a6fd317b` |
| authority-abort | runtime/authority_v5_g4a/service.py [source omitted from this derivative]：476–489 | `ced8a6fd317b` |
| outbox | runtime/authority_v5_g4a/proxy.py [source omitted from this derivative]：76–98 | `58f26a8f51da` |
| exposure-outcome | runtime/authority_v5_g4a/proxy.py [source omitted from this derivative]：277–338 | `58f26a8f51da` |
| pg-tx | aggregator_core/src/datastore.rs [source omitted from this derivative]：265–399 | `eb55dcd64b06` |
| control-epoch | src/commands/hadwc_v5.rs [source omitted from this derivative]：690–709 | `c815f7b9c341` |
| prepare-epoch | src/datastore/hadwc_v5.rs [source omitted from this derivative]：104–127 | `7b07ae066b2a` |
| native-identity | src/datastore/hadwc_v5.rs [source omitted from this derivative]：150–191 | `7b07ae066b2a` |
| journal | src/datastore/hadwc_v5.rs [source omitted from this derivative]：188–238 | `7b07ae066b2a` |
| native-authorization | src/datastore/hadwc_v5.rs [source omitted from this derivative]：262–328 | `7b07ae066b2a` |
| retained | aggregator_core/src/datastore.rs [source omitted from this derivative]：8430–8513 | `eb55dcd64b06` |
| receipt | src/commands/hadwc_v5.rs [source omitted from this derivative]：1263–1400 | `c815f7b9c341` |
| role-apply | src/commands/hadwc_v5.rs [source omitted from this derivative]：1402–1558 | `c815f7b9c341` |
| batch-add | src/commands/janus_interop_aggregator.rs [source omitted from this derivative]：3780–3851 | `b57fa7732f98` |
| reserve | src/datastore/hadwc_v5_export.rs [source omitted from this derivative]：38–133 | `9f75a0121baf` |
| bind-payload | src/datastore/hadwc_v5_export.rs [source omitted from this derivative]：136–162 | `9f75a0121baf` |
| dispatch | aggregator_core/src/datastore.rs [source omitted from this derivative]：7619–7676 | `eb55dcd64b06` |
| context-codec | runtime/g1_authority.py [source omitted from this derivative]：126–146 | `dbe0c086128b` |
| records-codec | runtime/authority_v5_g4a/codec.py [source omitted from this derivative]：185–206 | `961258d8b9da` |
| helper-reserve | aggregator/src/aggregator.rs [source omitted from this derivative]：4038–4077 | `54181d45dce3` |
| helper-send | aggregator/src/aggregator.rs [source omitted from this derivative]：4398–4425 | `54181d45dce3` |
| leader-send | aggregator/src/aggregator.rs [source omitted from this derivative]：3760–3791 | `54181d45dce3` |
| leader-before-helper | src/aggregator/collection_job_driver.rs [source omitted from this derivative]：304–311 | `c6504db3927a` |
| state-domain | circuits/hadwc_common_v5.circom [source omitted from this derivative]：23–34 | `fa8580bc4923` |
| commit-domain | circuits/hadwc_common_v5.circom [source omitted from this derivative]：35–48 | `fa8580bc4923` |
| distance-domain | circuits/hadwc_common_v5.circom [source omitted from this derivative]：49–63 | `fa8580bc4923` |
| genesis-relation | circuits/hadwc_genesis_v5.circom [source omitted from this derivative]：3–17 | `c2559a9de9b9` |
| transition-relation | circuits/hadwc_transition_v5.circom [source omitted from this derivative]：3–75 | `9988f8a7998a` |
| policy-relation | circuits/hadwc_policy_bounds_v5.circom [source omitted from this derivative]：4–12 | `78aa19c40e1f` |
| histogram-domain | src/flp/types.rs [source omitted from this derivative]：380–444 | `5284c42c8326` |
| original-output | src/vdaf/prio3.rs [source omitted from this derivative]：1392–1435 | `ef7d09e5d725` |
| opening-core | interop_binaries/src/hadwc_ct.rs [source omitted from this derivative]：153–187 | `70cea07d0fa0` |
| moment-core | interop_binaries/src/hadwc_ct.rs [source omitted from this derivative]：188–230 | `70cea07d0fa0` |
| batch-count-merge | src/datastore/models.rs [source omitted from this derivative]：1353–1357 | `f3b1ca2dd2fe` |
| batch-count-storage | src/datastore/models.rs [source omitted from this derivative]：1498–1502 | `f3b1ca2dd2fe` |

| leader-job-claim | runtime/janus-v5-g4a/aggregator_core/src/datastore.rs [source omitted from this derivative]：1312–1373 | `eb55dcd64b06` |
| leader-job-create | runtime/janus-v5-g4a/aggregator/src/aggregator/aggregation_job_creator.rs [source omitted from this derivative]：567–781 | `11c9703337b9` |
| leader-read-state | runtime/janus-v5-g4a/aggregator/src/aggregator/aggregation_job_driver.rs [source omitted from this derivative]：187–252 | `b6c30ff4f59d` |
| leader-peer-compute | runtime/janus-v5-g4a/aggregator/src/aggregator/aggregation_job_driver.rs [source omitted from this derivative]：769–1003 | `b6c30ff4f59d` |
| leader-transition-commit | runtime/janus-v5-g4a/aggregator/src/aggregator/aggregation_job_driver.rs [source omitted from this derivative]：982–999 | `b6c30ff4f59d` |
| leader-lease-fence | runtime/janus-v5-g4a/aggregator_core/src/datastore.rs [source omitted from this derivative]：2057–2111 | `eb55dcd64b06` |
| leader-retained-write | runtime/janus-v5-g4a/aggregator/src/aggregator/aggregation_job_writer.rs [source omitted from this derivative]：257–315 | `23d0aa5e1fcd` |

| collection-count-storage | runtime/janus-v5-g4a/aggregator_core/src/datastore.rs [source omitted from this derivative]：3512–3516 | `eb55dcd64b06` |
| helper-aggregate-count-storage | runtime/janus-v5-g4a/aggregator_core/src/datastore.rs [source omitted from this derivative]：4412–4416 | `eb55dcd64b06` |
| stack-secret-key-tag | tools/g4a_native_stack.py [source omitted from this derivative]：182–184 | `866030563c84` |
| driver-secret-key-tag | tools/g4a_native_drivers.py [source omitted from this derivative]：745–747 | `bb1d935484c1` |

## 8. 坏事件接口与不循环原则

source refinement部分是给定正确服务/存储、有效认证与已证明关系后的确定性安全命题；不把“业务全view安全”作为前提。密码错误分为：G16 generic碰撞/weakSE/ZK与affine异常，nativeFLP validity/HVZK/ROM及nonce/seed猜测，承诺binding/source-point模型，SHA碰撞，正确key认证伪造，带标签HPKE CCA及执行层前提。完整数值/查询总账由G4b专门文档负责，本文向其交付以下不能遗漏的计数约束：

- 所有失败proof尝试、genesis重复verification、warmup/zero/失败candidate、corrupt owner grinding、native RO查询及可观察重试都计入相应Q/N；不能只数最终R或成功commit。
- 同statement rerandomization不是新witness提取义务，走H/W/E来源；owner自持key不能收费为伪造。两role正确的C与主动role的P使用不同坏事件/执行结论。
- 所有规范encoding、body/package/context/P/R root、journal context、request hash等共用SHA256 collision预算，domain prefix避免跨类型歧义，不使它们变成独立随机函数。长度前缀/整数编码是确定性单射的分解，实际哈希绑定是另一个假设。
- context的两个128bit limbs完整保存256bit digest；每limb<2^128<p，严格重构，既无field reduction alias，也不应额外叠加两个“128bit截断碰撞”。固定96bit keytag不提供任意跨key/task替换安全；当前固定真实key、task/config/asset身份是范围限定。 实际tag还是`SHA256(verify_key)[:12]`，会泄露关于128bit secret key的至多96bit函数值；C的key猜测不能继续无条件按`Q5/2^128`收费。03/07用任意2^96值tag的分支并集界`min(1,2^96 Q5/2^128)`，不凭SHA collision resistance假定preimage难度或tag均衡。P已知key、所猜fresh nonce的事件仍有原128bit空间。若额外明确采用07的普通SHA OW128假设，可将上述信息界与具体OW归约优势取min；这项假设不从CR推出，也不把SHA另设为RO。
- APPLIED/status、count、checksum或opaque tag相等本身不证明同output，必须保留完整body/session/retained链。独立随机tag无需在全世界不同context间全球唯一；若新接口只凭tag检索，必须新增碰撞分析。
- 真实wallclock/timeout不是免费oracle；CT trace与精确拒绝计数模拟是G4a08给出的执行层推导。正确setup/陷门未知、存储持久性、ISA/编译器模型是明确条件，不藏成一个未解释ε。

本文不把任何尚待G3/G5测试的项写成PASS；这些条件下的参数化归纳与手工source精化已经给出，后续测试只验证具体故障/实现路径，不替代论证。
