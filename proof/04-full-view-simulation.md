# G4b：全业务视图的在线模拟与逐混合成本

日期：2026-10-18。固定00 [source omitted from this derivative]及安全游戏01的同一state实例。本文件展开冻结G4a的01 [source omitted from this derivative]/03 [source omitted from this derivative]，用[本轮03](03-native-privacy-and-query-ledger.md)的具体FLP/RO界取代未实例化的native项；02提供具体相关setup下的Groth16提取/ZK界，05提供源级prefix/refinement。结论是 **PROVED_IN_DECLARED_MODEL**。标准primitive Adv函数允许保留，目标组合安全或native隐私不是前提。

## 1. 输入权限、合法世界与完整view

μ只含事前固定profile/config/assets、task/key承诺、owner/uid/epoch及预算、窗口/slot、accepted-step索引、前驱/K引用拓扑、warmup/eligible、公开b、wire结构及外生资源预算。σ是敌手消息投递/丢弃/重试和独立executor coins。实际point/proof/ciphertext、T/receipt、hash/root/cert、verdict、commit/abort、发送是否被对方收到、执行时长均不能预置为μ或σ中的秘密答案。

合法H0/H1在每个诚实owner都有合法新genesis、每一步实际前驱与真实 `max(0,t−6)` anchor、正确范围/ADWC与公开b。状态点按**历史节点**只生成一次，prev/K/别名复制原点。不是只保证最终一窗等和。P/P+A在每一个允许首曝的完整R及先前输出上要求同一个认证声明histogram；包含sentinel的 `O_C(R)=Σ_(i∈R)e_(I_i)`。若最终Decoder删去D，则由公开b恢复D桶。A的接口 `O_A=∅`，允许两个世界的histogram不同。

view包含所有历史signals及认证链、两role全部输入密文/sidecars、所有proof/points/T、origin与Pending/Lock/Permit/receipt/commit/freeze/abort、被模型授予的DB/WAL/backup业务内容、outbox/HTTP回复与诊断、精确重放、所有前缀和模型内业务时间。P额外有一个静态恶意role的完整秘密/输入及Collector解密view；P+A再有正确authority的全部业务view，**没有其授权密钥**。A自己运行所需初始key正常由Setup生成，模拟器可执行其签名；这不等于把key交给P+A。

两role同时腐化、主动恶意authority、事后key替换/adaptive腐化、跨task复用inputshare、额外cohort输出、真实client即时完成时间、物理硬件攻击不在所选游戏中。它们不是以新leakage名目加入结论。

## 2. 全执行的表与原语优势接口

S维护这些**跨前缀共用**的表，不在每窗/重试重启：

- `H[(key_namespace,logical_relation,orderedSignals)]`：每次honest-source模拟proof的来源、origin、完整首次公开body/packet、native语义handle；同statement多次来源也各保留source标记。namespace包含02所有可见current/legacy key的身份；相同signals不能跨key被当成同statement。
- `W/E`：同一完整typed statement的先验已知/白盒提取见证。不能给malicious owner无witness模拟proof服务；02的同statement例外不是提取器。
- `RO[usage,seed,binders,offset]`：接受field、所有拒绝candidate、预取suffix与计数；logical descriptor/物理调用/bytes计数分列。
- `HPKE[fullTuple]`：实际recipient key/suite/info/AAD/enc/payload与唯一授权source override；配置alias解析到真实key。
- STATE节点/aliases、origin/body/slot/RID、P/R/L/A/M、真实head/K/quota、certificate、journal、retained/tag、receipt、outbox、唯一export snapshot/payload、exposure账本。

H表也含genesis/related-key prelude等没有native packet的proof来源；在下文native/aggregate公式里，H严格表示其中具实际诚实native source标记的transition报告子集。S_G16计全部proof模拟调用，N_shard只计native source，二者不能混用。仅有一个historical key的模拟proof并不自动得到当前任务的owner/origin/body身份。

原语Adv都用事件概率或两分布gap的具体游戏，并带全执行资源T和查询数：

| 记号 | 游戏与计数 |
| --- | --- |
| `Z_G16,alg(S,T)=0` | 02给出的projective数学honest proof→自适应模拟proof精确分布。实际affine失败/排除项 `A_G16(S)≤S(3p−2)/p²` 不放在此零项中，以下按每个hybrid端点并入B_route；即使generic碰撞已经覆盖identity，该并集上界的冗余仍安全。S计每个完整执行，不把局部8次attempt当全局cap。 |
| `X_G16(T,typedHandles,queries,S)` | 02的新exact statement白盒提取坏事件；每个hybrid端点的一整个执行使用一个generic collision/degree账本，非每报告乘一次未知SE项。 |
| `Adv_HPKE,k^cca2(T,1,D_k,L_k)` | 实际single-shot Base、固定suite/key、完整(info,AAD)标签的IND-CCA2；一个challenge、至多D_k合法decrypt查询及规定的byte预算。本文多ciphertexts用逐challenge归约相加。 |
| `Adv_Sig,k^euf-cma(T,S_k)` | 仅对手不知道私钥、也没有任意新签字授权的实际key集合 `K_sig,X` 使用EUF-CMA。S_k含该key所有真正新签字操作，缓存重放不新签；malicious owner/role持钥的签名不计伪造。A正常持有的authority授权秘密不在K_sig,A中：A按01正确运行且不注入额外签发，相关状态由同一算法生成，不能对该已知key调用EUF假设。P/P+A没有该授权秘密，按其实际未知key集合计。 |
| `Adv_SHA256^cr(T,Q_sha,B_sha)` | 一个SHA256函数的全执行碰撞游戏，所有context/package/body/root/certificate及外部查询合并。分成两个128bit limb是完整256bit编码，不用截断生日界。 |
| `Adv_Com^bind(T,Q_G)` | 需要排除同来源承诺被开成其他声明时的离散对数/binding事件；hiding本身完美，费用为0。02若已把该事件纳入typed generic/source-point账本，07选择其中一个账号，不重复收费。 |
| `b_N(N,Q_i)` | 03§5已实例化的单世界native RO编程界，δ_abort=0；不是primitive/nativeprivacy假设。 |

所有模拟/归约CPU及内部RO/签名/hash开销加入T、Q与bytes。各key只建一次signing/decrypt计数，所有SHA只建一个计数。primitive采用ROM或generic模型的限制保留；本文件不把具体SHA/TurboSHAKE称为无条件随机函数。底层固定suite的constant-time executor是另一个执行语义条件，不由IND-CCA/EUF自动推出。

C专用完整性对公开96bit verification-key tag使用03的`2κ_tag`及其明确OW128 primitive corollary；该项不加入本文件的隐私B_route。P/P+A原本允许事前知道整个native key，§5的fresh nonce界已在更强能力下成立；不能把C旧untagged猜测界复用为当前完整性数字。

令 `B_route` 为**一个hybrid端点的一整个执行**中 `X_G16 + A_G16 + Adv_SHA256^cr + Σ_(k∈K_sig,X) Adv_Sig,k + Adv_Com^bind + B_origin` 的统一上界，正确setup坏点也按02/07在同一端点账本纳入；origin的事前RID猜测可用 `N_RID·G_origin/2^128`，N_RID计全部诚实RID抽样/Origin预留尝试（包含失败而未native构包的尝试），G_origin计所有公布前的占位尝试，malicious自选RID不收费为随机。也可用公开honest-slot总预算保守替代N_RID；不能在没有支配关系时直接用N_shard省去失败预留。affine身份/失败与generic碰撞存在重叠时，这个有意冗余的并集界无需独立性；不会据“通常已包含”把实际formatter/statement差异省略。该定义没有证明各不同hybrid共用一个只失败一次的master coupling，因此不能自动跨全部hybrid只收一次。§6采用07的保守端点系数。native自己已有的诚实nonce重复/预查项不再放第二个同名事件。

## 3. source/statement与chosen-ciphertext的两层路由

先做真实public schema/context/owner/OriginCert/lock/permit及适用的Helper journal/Leader持久状态检查，再按source/statement分类，随后对需解密的non-H逐cipher分类。此顺序是组合算法，不是把所有情形说成互斥：

1. 原H完整body首次授权处理仅调用原语义handle；Helper exact retry返回已提交journal/receipt字节，Leader未提交/失lease重算按同原始handle和新收到的peer response执行，同lease fence至多提交一个transition。其完整challenge tuple不进CCA解密oracle，也不据不同peer response另造一个inputshare/source。
2. 同exact statement却改packet，由02的Lemma O固定owner/uid/epoch/window/step/RID及package digest，故改包须hash碰撞。只重随机proof而保持packet仍须新的honest owner签名并通过不可变body/slot/RID检查；否则拒绝或signature坏事件。
3. 新statement若不在H/W/E，02在线generic日志提取并入E；已在W/E则复用witness。提取给声明/STATE/MASK开口，**不给native密文plaintext**；之后仍须继续4–5。
4. 新malicious body若含原H完整HPKE tuple，native与sidecar AAD都含RID。诚实source在packet首次公开前已经持久取得该RID的OriginCert；origins.report_id全局唯一、rawRID=envelopeRID、完整身份/slot/RID与证书匹配。不同owner不能再占用同RID；冒用honest owner进签名坏事件，事前猜中RID进B_origin。直接native入口在HPKE/private处理之前核完整body/permit/exact tuple，不能绕开origin另开decrypt。
5. 其余ciphertext，包括相同enc/payload搬到另一个AAD/RID/key/info，属于合法非challenge查询。单挑战归约向honest-key oracle请求真实plaintext或bottom；它自行生成的其余keys直接解密。返回什么就真实运行codec/MASK/native算法，缓存actual retained、receipt及错误。不能无证明地将“改过的ciphertext”一律回bottom，亦不假设extractor或对手原先知道plaintext。

native label为 `dap-09 input share || Client || role`，AAD是task||metadata(RID,timestamp)||encoded public_share。sidecar info为 `SHTPC-HADWC-state-SIDECAR`，AAD包含task/RID/config/raw_report_digest/role/core_digest；core不含owner，所以不能省略第4项origin唯一性。开口明文是固定93B binary（mask16B、rho32B），AES-GCM payload109B，不是秘密decimal JSON。实际字段和最终003源pin沿G4a codec审查。

完整tuple排除的是actual key/suite/info/AAD/enc/payload。换config id但仍映射同key不能规避标记；同ciphertext改AAD则真是另一个oracle query。最终S自有honest HPKE keys，可以真实解non-H；单挑战归约却不知道其嵌入key，因此第5项必须用允许的decrypt oracle，不能混同两层知识。

## 4. P与增强P+A的在线S

固定静态恶意role c与诚实h。按源生成腐化角色已知的inputshare/plaintext、`r_c←F_q,ρ_c←Z_l`及真实MASK commitment；腐化role自己的HPKE密文须真实加密这些值。对H的隐藏历史节点/STATE、honest MASK、TICKET、RECEIPT按用途在满素数阶子群采样一次并保留引用。对于固定message，`ρ↦mG+ρH`是双射，故joint hiding精确；模拟器不求离散对数。已有已知开口的腐化MASK点不能随便换成随机点。

每H报告先取 `T←F_q`，用03的native kernel生成整个preparation transcript与orig corrupt vector v_c。native报告honest Finish时，缓存opaque tag并计算

`F(v)=Σ_(j=0)^10000 jv[j]`，`m_h=T−F(v_c^orig)−r_c`。

真实世界固定native view/r_c时，`r_h←F_q`令 `T=I+r_c+r_h` 均匀，且 `m_h=I−F(v_c^orig)+r_h`；所以 `(T,m_h)`恰为 `(U,U−F(v_c^orig)−r_c)`。这是与同一native随机变量相连的精确联合分布，不是两独立marginals。对恶意role任意adaptive m'_c，新增moment verdict为

`m'_c+m_h=T ⇔ m'_c=F(v_c^orig)+r_c`。

双方receipt均给敌手；上式未删除其中一份。错误绑定、session/nonce、quota/head等从实际模拟状态计算。root-abort/FLP/seed verdict由03已知verifier/rands得到；没有查询真实secret verdict。

non-H用§3取得真实honest plaintext、提取/已知声明x_j、native实际执行及honest receipt，缓存成功的 `w_h,j`。恶意owner+role可以伪造FLP或自身receipt，因此不能对non-H强制 `w_h,j=e_(x_j)−v_c,j`，也不要求S持有腐化role私钥。

完整R首曝时（05允许的reservation/bind边界），仅此时取得一次O_C。令 `R_H=R∩H,R_N=R\H`，计算

`V_h,R=O_C(R)−Σ_(j∈R_N)e_(x_j)−Σ_(i∈R_H)v_c,i^orig+Σ_(j∈R_N)w_h,j`。

第一项减掉已知non-H声明贡献后得到H允许总和，没有新增子集oracle。H identity-truncation给补份额，non-H加回实际honest输出。编码真实Field128 vector并以Collector HPKE封装，同snapshot重试用同plaintext；恶意role发送什么仍由它自己决定。P的actual Collector结果可以错误，不能借C的两正确role完整性来证明P。

S运行同一authority状态机、签名服务和DB/WAL/backup业务过程。P+A的额外authority view完全由同一已生成业务字节和状态产生；不增加密钥或理想输出。在每前缀L/P/R/M、实际head/K/quota和exposure按05推进，部分commit后abort不回滚历史。Helper的first-input/response journal将变化请求在private处理前拒绝；Leader则允许未提交工作按收到的不同Helper response重算，03的同Σ/z_h状态直接模拟全部Decide/seed反馈，最终writer/lease fence只允许一个已提交transition。不能把Helper的精确journal泛化为Leader每个CPU尝试都字节相同或事前conflict。

## 5. A的独立零输出S_A

S_A的初始输入没有O_C；它不通过先构建一个会查询aggregate的P+A模拟器再取marginal。它自行生成正确authority/role/Collector的独立初始keys（固定诚实owner keys则用相应理想签名oracle），运行真实public状态机，并直接构造如下随机view：

1. 对每历史节点生成一次均匀子群STATE，各用途承诺同样独立；所有aliases/K引用复制。两MASK均隐藏，不向A给开口。
2. 每H独立取 `T,u←F_q`，设 `m_A=u,m_R=T−u`。任意实际原生v_A,v_R固定后，真实 `(r_A,r_R)↦(T,m_A)`是F_q²双射，故该两receipt联合分布精确且无需aggregate。
3. Public joint parts由独立secret blind的U7输出直接模拟/编程；未知seed命中仍计03账本。为可能可见的prep生命周期，独立生成03的FLP/query/seed状态，root命中就同错误；诚实合法source其余检查成功。也可内部选一个**不向A公开**的均匀anchor share v_A，再令 `r_A=u−F(v_A)`、用Σ减其Q_2产生另一verifier；这里只用03的无Agg prefix kernel，永不调用aggregate接口。
4. 双方native input与sidecar都改为等长dummy HPKE，source处理使用标记语义override；non-H由自有honest keys真实解密及执行。若A可见最终aggregate ciphertext，两role→Collector的该ciphertext也用固定160016B dummy plaintext的IND-CCA混合隐藏。A不是Collector，不得到其解密key。
5. `export-status`仅SQL EXISTS；私有export payload为固定160016B BYTEA且禁压缩。S_A只需公开长度、存在位与调度生成相关执行工作，不加载未知aggregate再伪称已模拟。A自己的业务DB/WAL/backup由前述模拟业务字节真实产生；它没有诚实role私有DB或地址trace。

步骤2与3仍共用同一T/receipt，而非随机重抽局部marginal。原生输出handle只需要其存在/类型/固定长度，不需要解开数值。理想O_A始终为空，两个比较世界的聚合可不同；对恶意客户端已知/可解密的输入真实执行也不隐含未知诚实aggregate。

## 6. 固定一世界的hybrid表与费用

每一hybrid在报告**首次公开之前**构造完整一致body。已经交付或持久的body不被修改。HPKE相邻归约在固定合法世界知道原始m0，用原source记录处理prep/receipt；dummy密文没有被声称仍能在未修改真实role中解出m0。最后才由未知I也可运行的S接管。

| 变换 | 联合构造/必要信息 | 单世界费用 |
| --- | --- | --- |
| 保留source/route且排除首次不合法替换 | §3公检查、H/W/E与02在线提取；malicious-key不是伪造 | 相邻实验各端点的bad概率≤`B_route`；以下统一乘端点数 |
| 真实honest proofs→模拟proofs | statement先固定；保存历史引用；每次actual sim oracle调用计S | 数学 `Z_G16,alg=0`；实际affine排除费用已入每端B_route，不另在此行重加 |
| 隐藏HPKE plaintext逐个dummy | 同长度；更新raw/package/core/context、模拟proof、body/owner签名；先于登记；固定source override | `Σ_challenges Adv_HPKE,k^cca2(T',1,D_k,L_k)` |
| Native RO/原始随机份额→03 kernel | 保持所有usage/offset、允许query与nonce/key限制，full verifier强sim | `b_N`，内含δ_abort=0；不是额外native项 |
| 历史与其它隐藏点、T/receipt联动 | 满子群双射、原始inputshare identity、同r_c/known MASK点保持真实 | 0 |
| nonce/candidate trace、规范codec/hash/signature/业务DB/diagnostics/time | 已知随机view与受审执行轨迹的同一后处理 | 0（模型前提不加概率未知项） |
| 首次完整R aggregate | P/P+A用§4的H/non-H公式；A无输出，已在HPKE行隐藏出站aggregate密文 | 0之外只用前行已列HPKE挑战 |

这里的“更新模拟proof”指另一个相邻实验中同一report首次公开时生成的proof，**不是**向敌手追加事后替换的proof或隐匿旧query。S是每个完整hybrid执行的全部模拟proof调用数上界；可保守把内部额外调用全部计入，但不能把多个互斥实验的输出当实际同时出现。02的全执行提取坏事件使用所处hybrid的S/typed handles统一上界。

设N为H shard次数、E为允许的唯一cohort首曝数（本实例E≤1），则P/P+A需隐藏的honest ciphertext源数 `C_HPKE≤2N`：每H一个honest native inputshare、一个honest mask sidecar。A若每role仅封装一次为 `C_HPKE≤4N+2E`：两role两种输入，及至多两份aggregate ciphertext。相同snapshot被重新加密多次的A观察view须计实际新封装次数 `E_enc,A`，准确上界为 `4N+E_enc,A`；**不能用E≤1抹掉无限重加密的工作**。若游戏限制有限HTTP/external资源，E_enc,A由该预算给出。P的额外出站HPKE已知plaintext直接生成，不收费为隐藏挑战。所有honest recipients的D_k解密次数及byte预算仍合入对应单挑战游戏。

为不依赖未证明的跨hybrid坏事件去重，统一逐一展开C_X个cipher-hop和以下10个macro-hop：

| 宏hop | 对应数学步骤 | 该hop自身单侧损失 |
| --- | --- | --- |
| 1 | source-proof采样 | 数学ZK为0；affine已进入每端B_route |
| 2 | nonce去重 | `N²/W` |
| 3 | initial RO编程 | `N[Q4+2(Q3+Q6+Q7)+Q5]/W` |
| 4 | shares/parts编程 | `N[Q1+Q2+2Q7]/W` |
| 5 | prover coins移除 | `NQ4/W` |
| 6 | FLP full-verifier | `Nδ_abort=0` |
| 7 | hidden point/receipt联合 | 0，满子群双射和联合moment等式 |
| 8 | raw trace耦合 | 0，计数/接受值精确分解及同流缓存 |
| 9 | 业务/首曝后处理 | 0，完整R、来源路由和标准executor |
| 10 | strict-PPT截断 | `Tail_sum`，候选搜索前缀/32预取预算分列 |

每个native有损子hop分别比较，不把它们藏在一个没有足够端点的大macro内。各native自身损失仍仅相加为b_N，**不再乘M_X**；0费用macro允许保守保留。每一相邻实验两端的route失败各≤B_route，game-playing triangle给系数 `M_X=2(C_X+10)`。全部端点使用相同外生T/Q/typed-handle上界，不要求其bad事件独立或在同一真实执行中同时出现。每端仍只有一个SHA256全调用账号；乘端点数并不是为字段假定独立hash。若将来证明更紧master coupling可以减少M，当前不借这种尚未给出的结论。

本轮budget-contract选择strict-PPT模拟器；单世界view距离写为

`e_X ≤ M_X B_route + Σ_(j=1)^(C_HPKE,X) Adv_HPKE,k(j)^cca2(T_j,1,D_k(j),L_j) + b_N + Tail_sum`，

X为A、P或P+A，S_A使用独立构造而不是带输出simulator的marginal。Groth16的数学ZK精确，实际affine失败项统一进入每端B_route后乘M_X；不再在式外另加一遍affine。`Tail_sum=Σ_fresh_hidden_stream Tail(L_s,L_s+128)`，至多5N个fresh field streams；03§7给出完全实例化公式和更宽的闭式上界。若另声明expected-PPT精确几何S，才可删去Tail_sum，同时改写相应归约时间约定。两合法世界之间以同一个无I的S及相同O_C比较，优势≤2e_X（若07采用标准单侧Adv定义，则按它的归一化统一因子）。native细分损失按03合计b_N；route按M_X端点保守收费，FLP soundness和root completeness均不放入这个privacy界。

## 7. 时序、诊断、abort与重放的在线性

原生未知inputshare/proof/MASK/retained的秘密算术由G4a实际003CT审查和native Field/FFT/FLP路径固定工作覆盖。03为fresh hidden XOF流附加与接受field独立的几何计数；重复流复用同完整candidate bytes，已知/自选seed直接展开。r根检查是已模拟query coin的后处理；FLP/seed最后verdict是已知Σ/peer消息的后处理。

秘密sidecar明文固定93B，role无secret decimal parser；retained及aggregate固定10001×16B；实际secret BYTEA禁内容压缩、WAL compression off；status EXISTS不读未知payload。公开moment、point、proof/cert的decimal/JSON长度由模拟的**同一联合字节**产生。不能先把真实长度/时间给S，再说它由这些字节导出。

在00/08标准executor中，primitive固定延迟语义、受审地址/IO、公开键和长度、外生存储/网络coins给出执行工作τ；业务HTTP结束/timeout/abort为 `Post(τ,敌手调度,外生coins)`。authority在已模拟字节上可变时间运行同一PPT算法，S亦真实执行。τ用于内部论证，并未额外授予A诚实role私有地址或DB view。所有物理data-dependent延迟、cache共驻、power/EM、故障、client本地即时生成时间不由该模型保证。

事务可能回滚后重算。Helper有显式first-input/response journal；Leader的Tx外`leader_continued`可能使用与上次不同的Helper response，最终 `step_aggregation_job_2` 同事务写结果及按lease token/expiry释放lease，失lease则不能提交。这里保证的是唯一已提交状态转换，**不是**每个未提交CPU输入分支均预先journal。固定report/body/key/nonce、原始shares和已提交状态使honest query仍对应同一Σ/z_h；每次不同peer response的Decide/seed结果由该固定随机变量和敌手消息直接计算，原RO候选流复用，不开启新source/新query coins。实际重算次数、raw bytes及hash/signature工作继续计入外生预算；C中正确Helper对同输入的回复缓存一致。响应发送与提交/lease关系按05的逐路径精化处理，未提交工作不被当作新的retained/admission。发送后丢ack不取消已经发生的暴露；恢复从同一持久业务状态继续，不允许敌手回退库。

因此归纳于每一个prefix：S的状态与下一业务输出只依μ、独立coins、已收到敌手消息、已有理想完整R输出及外生scheduler。秘密verdict、真实time或最终SUCCESS从未作为额外oracle输入。首曝后collect失败仍保留O_C/exposure；之前abort不查询aggregate，不能凭将来等和来豁免提前的子集输出。

## 8. 检查与交付

预算合同给出N/Q/bytes/physical calls定义及primitive调用接口，03的公开exact检查记录FLP、constant split、candidate trace和H/non-H输出的有限证据。它们不代替本文件逐hybrid归约。G4a frozen proofs/source/binary只读匹配，新的文档/脚本/输出由本轮交付清单固定SHA。07以这里的单侧接口组合全部账本，不把旧G4a的条件摘要或任何检查PASS当作未写步骤的证明。
