# G4b：完整安全实验、理想接口与预算语义

版本：2026-10-18，固定G4a加固实例。本文件给出后续定理使用的完整实验；实验中的受支持输入、可信服务与执行模型属于明确前提。预算和泄漏在挑战之前确定，不能由运行后观察到的成功、错误或耗时反向定义。

## 1. 参数、参与方与setup实验

令D=10000，原生空间V=F_q^(D+1)，q=340282366920938462946865773367900766209；e_j为其标准基。认证声明i的公开贡献位b_i∈{0,1}、隐藏cell坐标(cx_i,cy_i)∈[0,99]^2定义x_i=b_i(100cy_i+cx_i)+(1−b_i)D。原生一热有效域是E={e_0,...,e_D}；最终显示直方图删除sentinel D。

参与方为owner集合U、正确admission authority A、两个aggregator角色S_0/S_1、Collector C及Decoder。task/profile/config、owner/epoch enrollment、角色与Collector的HPKE key handle、原生verify key、当前两关系CRS和全部生成器在任何诚实测量前固定；历史公开的第三个相关genesis key也属于02的攻击者auxiliary CRS，但不成为当前接受关系。本实例不允许挑战后换key或迁移旧history。静态腐化集在挑战前固定。接收公钥由实际config ID解析到同一key handle，不能把alias当成新key。Groth16源群的素数阶/电路域模数记p；BabyJub素数子群阶另记ℓ；原生Field128的阶记q，三者不混用。

Setup按02指定的正确多关系setup分布采样，输出公共CRS、key/config/manifest身份；安全归约的SimSetup可持有模拟trapdoor。真实authority不持有该trapdoor，也没有从冻结公开CRS恢复trapdoor的算法。对已保存development资产的实例解释以其来自正确独立采样且陷门未泄露为条件，测试/哈希一致性不认证该条件。公共raw phase1、initial/final key、contribution PoK与所有允许source points都进入02的typed generic运算模型；不可暗中授予未知相关scalar或离散对数oracle。

诚实owner的STATE/MASK/TICKET承诺随机因子各自在F_ℓ均匀独立；receipt加性mask在F_q均匀独立，二者不混为一个随机域。RID由CSPRNG生成16B，origin在报告公开前先持久预留RID，RID在task中全局唯一。native sharding使用单proof、两方Prio3Histogram(10001,100)、Field128、XofTurboShake128、16B seed/nonce；以实际VDAF-08/DAP-09域编码为准。native XOF在03的programmable random-oracle模型中分析；底层签名/哈希/HPKE与独立曲线分别使用各自明确假设，不从一个原语的安全性免费推出另一个原语的安全性。

## 2. 有限合法历史与公开骨架

在有限执行预算B内，挑战环境为每个诚实owner给出两个完整合法历史H_0/H_1。每个世界均有自己的合法genesis、规范有界坐标、STATE opening、前驱与真实K=max(0,t−6)锚点及完整有限候选链；每步满足ADWC整数关系，b=0也执行全部状态约束。任何跨window延续都从实际已commit的head继续，pending仅是候选。对手不能根据先前收到的诚实报告再改变该source所用的挑战输入；允许依据既有view选择下一次来自预定合法历史的source请求。

两世界必须匹配公开骨架μ：owner/epoch、固定task/config/asset/key身份、window、预定slot/accepted-step资格与公开b、完整前驱/K引用拓扑、包的类型/长度规则、预定交付边界/截止和静态腐化集。μ不包含挑战后commit/abort集合、实际verdict、回执、随机承诺点、证明实际编码长度、真实时间或个体测量。随机点/证明/密文的长度从本次模拟字节实际计算；相同历史节点只采样一次并重复引用，不能用“公开metadata”掩盖它们的待模拟相关性。

对手可自持腐化owner密钥，任意构造自己的非honest-source报告和chosen ciphertext、选择消息顺序/延迟/重试/peer input、丢弃或终止。诚实报告通过独立认证保密信道按事前input-ready计划完整交付authority；本地witness/prove完成时间不在在线交互观测范围。直接在测量相关计算完成后立即发送、从而暴露本地生成时长的部署不继承该边界。

## 3. 完整记录及理想状态F_lock

一个record的类型包含(profile/config/asset/task/key-tag、owner/epoch、window/step、RID/body/statement/package身份、prev/K/next承诺、资格/b、native aggregation parameter)；字段规范编码以冻结source为准。对一个selector，P为锁定完整record映射，R=eligible(P)，L为实际commit映射，A_L=eligible(L)。角色s的本地commit投影为L_s、实际apply集合为M_s。每条M_s另绑定不可变body→native job/protected step→retained output/tag→consumed membership。锁内不包含尚未产生的session或输出，后者由receipt/CommitCert/reservation附加连接。

F_lock维护如下单调状态，不提供秘密verdict oracle：

1. Register：验证规范公开编码/origin/body绑定及关系witness，保存独立完整提交的有限候选图；未锁时可按公开规则拒绝或整窗失败。每slot/RID只有一body，诚实source与对手source分表记录。
2. Lock：只在μ的预定边界且完整P均已持久交付时锁P/R；缺项导致等待或整窗abort，不能根据准备反馈删R。登记和锁不改变实际history。
3. Permit：按实际head/K/version/quota校验依赖和唯一body，签发与锁相同上下文的permit；尚未commit的后继不变成真实历史。
4. Prepare：固定报告/task/RID/body/nonce/aggregation parameter及已提交native状态。Helper以显式journal持久锁定首次job/step/peer input及response，exact retry返回同持久字节，变化输入/新job在私密处理前公开conflict。Leader的原生job/lease fence保证至多一个已提交transition；它的事务外未提交计算可以在重试时收到不同Helper响应，不保证这些计算都先公开conflict，也不保证每条协议网络消息先持久为Helper式journal。所有这类反馈用03同一个已固定full verifier/nonce/joint/query状态模拟；未提交工作不推进接纳history/retained/apply，实际调用/时序全部计入预算。相同RO描述符复用完整raw候选流。状态机只在最终原子提交后推进接受的native状态，业务receipt/retained响应的持久边界见05。未知测量相关verdict不是F_lock的免费输入。
5. Receipt/Commit：生成同一输出的masked receipt；两回执绑定和moment检查后，在原子head/K/version/quota CAS成功时把唯一合法后继加入L。对手角色可签自己的任意receipt，P实验必须模拟其判决而非假设它诚实。失败保留既有commit和已耗quota。
6. Apply：正确角色只使用CommitCert连接的同一retained output，eligible项加入M_s一次；warmup只推进状态，eligible b=0仍是R/M成员。
7. Reserve/Send：要求同类型完整L_s=P、eligible(L_s)=R、M_s=R及所有retained links相符，持久保留唯一selector/snapshot及实际明文，再发送诚实share；缓存路径也经过同一门。重加密可以变ciphertext，不能变集合或明文。
8. Abort/Recovery：未暴露时终止为PRE_EXPOSURE_ABORT，已暴露或可能发送时不得声称零暴露；EXPOSED_COLLECTION_FAILED保留暴露账本和同一snapshot。恢复只能继续同一持久状态，不能回滚history/quota或清除journal tombstone。

本实例的task dispatch只允许一个可见selector，故每task首次语义输出查询数E≤1。多窗口历史可以存在，但当前源码不证明同task多个不同cohort的重复发布。更一般的理想多cohort必须对每个已允许集合分别保持等和并新增查询账本，不能由最终一次等和推出。

## 4. C：语义闭合实验

Exp_C(Budget,B)：Setup后，B控制所有恶意owner及消息投递；authority、两个aggregator、Finalizer、Collector/Decoder按协议正确执行。原生verification key K由正确setup事前均匀采样16B，不直接授予恶意客户端；实际公开`prefix96(SHA256(K))`，其相关泄漏按03/07计入key猜测，不能当仍独立128bit隐藏。K的其余C可见使用仅是U5 query-randomness接口，role私有DB/admin配置不授予C；不得从P的腐化role能力推得C对手也知完整K。允许进程停止/重启，但其可信存储、事务原子性与恢复不回退已commit状态为执行前提。B赢当某前缀出现诚实可解密share不属于完整固定R的唯一持久snapshot，或某成功Decoder输出不等于完整R认证声明的Σb_i e_(cell_i)，或L不是同owner合法ADWC顺序历史。

ε_C=Pr[Exp_C=1]。05给确定性归纳：在排除02提取、承诺绑定、正确主体认证/规范哈希、03实际native validity错误事件后不可能赢。服务错误、掉盘、管理员改库或另一编译器未满足执行语义不被塞进一个未定义可忽略ε。

C不声称malicious role仍输出正确：一个腐化aggregator可伪造自己的moment或最终share，因此完整性与下节隐私使用不同腐化集。

## 5. A：authority零输出实验

Exp_A^b：Setup、静态腐化owner及合法世界H_b后，正确authority处理μ允许的交互。观察者获得authority全部业务输入/输出、公signals/proof/body/ciphertexts/两回执/diagnostics、业务DB/WAL/backups、公开状态和在线时序。它知道自己正常运行持有的authority状态与授权秘密，但不获得任一aggregator解密key、私有输入/输出/DB，也不因发生collection取得aggregate。A自身始终被动且正确签发：动作接口不允许它把已知authority密钥用于额外控制证书、换配置或绕过状态机；也不允许与恶意owner串通注入这种新authority签名。它可对持有的key作离线计算并据此区分view。对其正常签名可由Setup或honest signing接口模拟；不向另一个观察角色扩散此私钥。其已知的authority key不属于07不可伪造归约的未知密钥集合。

理想Sim_A输入(Setup服务接口、μ、对手已发送消息和自己的coins)，其理想输出权限O_A=∅。它必须在线生成整个view，不可在结束后请求histogram或真实时间/abort bit来补造早期prefix。H_0/H_1不要求aggregate相同，故此实验不能由一个已使用aggregate的P+A simulator简单投影得到。

记Δ_A(b)=SD/计算区分距离(Real_A(H_b),Ideal_A(μ))，优势按两分布输出bit概率之差的绝对值定义。总两世界优势至多Δ_A(0)+Δ_A(1)。04给零输出simulator和逐hybrid差异；完美Pedersen hiding及(T,m_0,m_1)联合分布不收费，primitive替换与RO坏事件按07单列。

## 6. P及P+A：一个主动角色与Collector

Exp_P^b：B静态控制一个aggregator c及Collector，并可控制腐化owner；authority与角色h正确。B得到c的原始可解密native/sidecar、全部发送与收到的peer消息、公业务消息和Collector实际可得结果。B可以伪造自己的FLP share、joint part、receipt或aggregate并选择任意中止。首次honest share一旦可解密，即进入允许暴露账本，无论最终collection是否成功。

Exp_(P+A)^b额外给出正确authority的完整业务view，但不给authority授权私钥，也不允许它恶意签发。它不与A实验混同；A实验本来知道自己的内部秘密，增强实验只是业务view共享。

对每个实际获准首次暴露的完整R，理想接口O_C(R)=Σ_(i∈R)e_(x_i)，含sentinel、task/selector与暴露账本。若只提供删sentinel向量，由公开b和R恢复D桶。两合法世界对所有允许暴露R的O_C值必须相同；不要求c伪造的实际Collector输出相同，也不假设腐化source原生输出遵守声明。

将source分为H（由挑战环境诚实生成并记入模拟查询表）和Bsrc=R\H（对手来源）。02提取或先验知道Bsrc的声明x_j；合法HPKE解密及实际native执行给出honest retained w_(h,j)。仅对i∈H有在honest Finish时v_(h,i)=e_(x_i)−v_(c,i)^orig。于是合法理想查询足以计算真正honest aggregate：

V_h(R)=O_C(R)−Σ_(j∈Bsrc)e_(x_j)−Σ_(i∈R∩H)v_(c,i)^orig+Σ_(j∈Bsrc)w_(h,j)。

该式不新增H子集oracle，也不把C的双方正确完整性偷渡进P；对手伪造最终share依其自身动作继续输出。04的Sim_P/Sim_(P+A)在授权R首次暴露前不得查询O_C，之后只可缓存同一值/明文。定义Δ_P(b)、Δ_(P+A)(b)与上节相同，07分别给逐世界误差及两世界之和。

## 7. 预算B与优势函数

预算B在Setup/挑战前公开给定，所有算法至多运行T步、发出B中相应次数和总长度的消息；达到预算则按公开规则停止。预算是有限安全实验的资源上限，**不是声称源码对全部接口都有同样硬cap**。特别是genesis先verify再判exact retry，不能用每origin8次的transition cap上界全部验证。

至少分别计：诚实source genesis数N_g、transition构包数N_shard（含warmup、zero、未prepare、未进入最后R、失败和已prepared后abort的报告）；实际Groth16 verify数Q_g/Q_t及每hybrid的模拟查询数S_g/S_t/S_old；typed generic的初始/派生handles与equality tests；每key真实签名/验证查询次数和总消息长度；同一个SHA256函数所有不同消息的总Q_H（包括domain separation、package/context/body/roots/journal）；每recipient key labelled HPKE的encrypt/decrypt次数与字节预算；七种native XOF的不同输入/输出候选/已知seed重算次数；诚实RID及隐藏seed/blind生成次数和敌手猜测数；每唯一受保护prepare attempt与首次cohort暴露数。所有related-key模拟查询均计入S=S_g+S_t+S_old，即使old key不会被当前应用接受；未开放的old-key模拟API不能自动假设存在。

exact重放不增加逻辑prepare或允许输出数，但实际hash/signature/HTTP/RO重算仍按其真实工作计数；通过cache读相同RO输入不增加新的独立随机样本，首次曾查询和多次重读分开。03给raw-candidate与accepted-field数量关系及公开PPT截断尾界，02给generic分母/degree和handles界。07逐项命名并指定单位，所有最终公式须为显式有限表达式，不能以O()或未定义“总组合安全ε”结束。

## 8. 标准执行层与时序观测

在线执行器按冻结目标的instruction/address/IO语义产生内部trace；integer加减/固定位宽乘法/条件选择、固定长度拷贝和已指定密码primitive满足标准常量时间语义，编译器保持已审的秘密数据流。程序自制receipt core/native字段/判决路径的对应由实际source及binary审查给出，不能用primitive安全假设跳过。

拒绝采样原始流按(usage,key/seed,binders,offset)缓存；几何拒绝计数与accepted values联合生成，不能独立重抽同seed或把真实timeout交给simulator。秘密BYTEA按公开key和固定长度访问、禁内容压缩，export binary固定长度、status只EXISTS；A没有诚实角色私有DB或地址trace。

墙钟/timeout/业务abort为内部可模拟工作与对手scheduler及世界独立executor coins的因果后处理，simulator运行同样后处理。该模型不额外授予真实secret-dependent时刻oracle；共驻cache、power/EM、故障、值相关硬件延迟、任意target/compiler以及本地prover生成时间不由此模型覆盖。不同机器需重新给出执行映射，不能由本轮functional witness代替。

## 9. 验收边界

理论实验和05的正确执行refinement不等价于G3/G5全campaign已通过；G4b冻结同一明确实例并记录后续改动影响。已有G4a关键证明继续为历史事实，本轮给完整展开与精确账本；若发现实质新问题，保留旧交付，给具体修订/新源与受影响验收，不悄悄刷新旧hash。本文不建立物理位置真实性、Sybil resistance、DP、持续可用性或productionsetup认证。
