# G4b：完整组合定理、有限预算与显式误差

日期：2026-10-18。对象是00/01固定的G4a加固实例。本文将02–06的论证组合为C、A、P、P+A四个结论，给出每个概率项的有限表达式与归约接口。模型为typed opaque generic bilinear groups、可编程原生XOF随机预言机、正确setup/持久存储及受审标准executor；不是对任意真实曲线算法或硬件的无条件定理。

## 1. 记号与资源实验

令`clip(z)=min(1,max(0,z))`、`choose2(h)=h(h−1)/2`。三个不同的域为：

- Groth16源群阶/电路域 `p=21888242871839275222246405745257275088548364400416034343698204186575808495617`；
- BabyJub承诺素子群阶 `ℓ=2736030358979909402780800718157159386076813972158567259200215660948447373041`；
- native Field128 `q=340282366920938462946865773367900766209`；seed/nonce空间 `W=2^128`，`ρ=(W−q)/W`。

预算B在挑战前给定。每个数都是整个有限实验（含诚实构包、旧related-key prelude、攻击者离线工作、失败、未prepare报告、warmup、zero、回滚重算和重试）的公开非负整数上限，不是宣称source强制这些cap。对超过外生预算的执行，游戏停止；不能在看到结果后只把成功子集拿来代入。

| 量 | 精确定义/单位 |
| --- | --- |
| `N=N_shard` | 全部H诚实native构包source数，含未prepare的公开包；不是最终R大小。 |
| `S_g,S_t,S_l` | 三key下全部fresh外部sourceproof，包括真实honest proof的02精确重参数化与模拟proof；字节缓存不增S。genesis没有native包也计S。 |
| `V_g,V_t,V_l,Q_G1,Q_G2,Q_GT,Q_pair,I1,I2` | 02的全部验证/typed oracle/source输出计数；本文件将02的Q1/Q2/QT/Qpair依次改名为Q_G1/Q_G2/Q_GT/Q_pair，避免与native usage的Q_i同名。失败genesis verification及额外offline运算不能遗漏。 |
| `Q_i,Q=Σ_(i=1)^7Q_i` | 实际usage i的全部XOF输入/扩展调用，外部和内部均计；raw candidates及bytes另记，不能拿接受field个数当Q。 |
| `G5_ext≤Q5` | 外部敌手U5查询里实际出现的16B候选key数；诚实内部使用正确K的hidden-handle调用不是敌手猜测。 |
| `P_att` | C中不同受保护完整input的首次攻击prepare尝试数，含失败；物理rollback不产生新input，但其实际RO/CPU工作仍入Q/T。 |
| `N_RID,G_origin` | 全部诚实RID抽样/Origin预留尝试（含预留拒绝后未构包）；诚实RID首次公布前的恶意占位猜测次数。恶意自选RID不是均匀随机变量。 |
| `E≤1` | 固定task允许的完整cohort语义首曝数，collection失败不重置。 |
| `E_enc,A` | A可见的新honest aggregate HPKE封装次数，同snapshot重加密也计；不由E单独界定。 |
| `S_sig[k],D_hpke[k],L_hpke[k]` | 每个实际key的签名、合法非challenge解密次数及全部吸收/输出/明文字节上限。 |
| `Q_sha,B_sha,Q_Com` | 同一SHA256函数全用途调用/bytes；五类承诺的全部已知scalar群运算、开口/比较与生成工作。 |

每个hybrid端点都用同一B的上界。互斥端点的handles不能被说成同一个真实执行同时出现；§5显式用端点并集系数处理。资源`T_red,j`是第j个指定归约在B及下述strict截断下的实际最长抽象机执行步数；安全函数取这个数或其事前更大上界。归约为02维护有限线性表示日志、03的定长FLP/RO模拟和04的单challenge路由，没有rewind或无界oracle。所有消息、群输出、RO字节与循环均由B和§3的raw前缀截断界定，故这个资源是有限的；primitive优势不能只代入攻击者运行时间而省略归约工作。本文不把抽象步数当本机性能测量。

下文没有下标G的`Q1,…,Q7`只表示03的native XOF usage，不能与generic群输出数合并为同一输入。两类预算可以由共同总时间上界分别约束，但其计数单位不同。

## 2. 一整个端点的密码坏事件账本

### 2.1 相关CRS、generic碰撞与affine

当前genesis、transition和历史genesis共三个独立delta。02逐section枚举所有公开材料，初始保守handle数是`(330974,80986,5)`；共同分母是三个delta的乘积。清分母degree为`(D1,D2,DT)=(32769,16383,49152)`，不是随模拟查询数再乘分母。

写`S=S_g+S_t+S_l`、`V=V_g+V_t+V_l`，并定义

```
H1 = 330974 + 2S + Q_G1 + I1 + 13V_g + 53V_t + 13V_l
H2 =  80986 +  S + Q_G2 + I2 + V
HT =      5 + Q_pair + Q_GT + 7V
g_coll = clip((32769 choose2(H1) + 16383 choose2(H2)
               + 49152 choose2(HT)) / (p−16385))
g_aff  = clip(S(3p−2)/p²).
```

若setup先从全F_p采样，`g_setup=1−((p−16385)/p)((p−1)/p)^5`；若游戏直接从02正确好域条件采样，`g_setup=0`。本轮账本选择后者，另外保留前者的精确函数，便于改变实验时明确收费。正确独立熵、未知陷门与未泄露不是这个采样坏点概率所认证的事实。

`g=clip(g_setup+g_coll+g_aff)`。identity与全typed表达式比较已经包含于`g_coll`，因此保留`g_aff`是有意的保守冗余上界；不要求它与碰撞事件独立，也不称它们概率相等。每个端点均使用同一上界g，避免只给第一次宏hop收费后遗失其它statement下的affine异常。

02的提取器对非H/W/E新statement返回witness或进入g事件；同statement只指认其完整key namespace的H来源。真实外部honest proof也计S：固定合法statement后，独立r/s可双射成μ/ν，C由验证式唯一确定，正是02的source公式。没有调用SimAPI不表示S可取0。运行时可拒绝identity而影响成功率，这不构成一次错误接纳；在C也保留g_aff只使界更松。

### 2.2 SHA、认证和承诺binding

`h=Adv_SHA256^cr(T_red, Q_sha, B_sha)`是一整个执行中对**一个**SHA256函数找到任意两条不同消息同digest的概率上界。source/package/body/context/record/P/R root/request/journal/signature-message等都入该同一账号。规范长度前缀与字段范围的确定性单射不收费；完整digest拆成两个128bit limb没有额外截断碰撞项。

令`K_X`为实验X中敌手未知且用于正确主体接纳的实际签名key集合，

`a_X=Σ_(k∈K_X) Adv_EUF-CMA,k(T_red,k,S_sig[k],message_bytes[k])`。

对任何first accepted新签名，归约输出该key下未向签名oracle请求过的完整message/signature；如签过message却其不同字段被解析为另一上下文，则由规范codec或h处理。只需EUF，不用strong-EUF；同message换签名也不能改变其BODY/证书意义。每key归约可服务该实验其余全部keys，求和是按实际key，无须再乘报告数。恶意owner/role自持key不入K_X。A虽知道自身authority key，其动作接口仍只准被动观察正确authority，不允许额外authority控制消息；该key不入K_A，也不靠它的EUF证明A。P/P+A未获authority key，可把它纳入K_P。

`c=Adv_Pedersen5^bind(T_red,Q_Com)`为五用途（STATE、MASK_A、MASK_R、TICKET、RECEIPT）的普通多实例计算binding游戏：给实际事前固定的五对素子群非identity生成器及独立其它公共参数，输出一个用途下同一点的两组规范开口`(m,r)≠(m',r')`且`m≠m' mod ℓ`。规范message都小于ℓ。由

`(m−m')G+(r−r')H=0`

可知`r≠r'`，并直接求`log_G(H)=−(m−m')/(r−r') mod ℓ`。这说明该账号是标准生成器离散对数/binding假设，非“目标wrapper安全”假设；可进一步按五个被猜中用途归约求和。真实hash-to-group生成器的未知离散对数与独立source模型仍是前提；文件相等不认证熵或未知log。诚实满F_ℓ盲化使隐藏性精确，其隐私费用为0。本文不把BabyJub binding偷塞进另一个BN254 generic碰撞界。

事前origin猜测用`o=clip(N_RID G_origin/W)`。native诚实nonce重复已在§3计入，不在o再加一次同生日项。不同事件可有重叠，采用并集上界不要求独立。保守的单端点路由界是

`B_X=clip(g+h+a_X+c+o)`。                         (R)

它在该端点覆盖整个有限执行，绝不对每个accepted proof重复乘g；跨不同端点则按§5明示乘数。

## 3. native三类界和严格模拟时间

03从实际Histogram源码重证强HVZK。固定128节点、wire degree127、gadget degree254、proof455、verifier202，真实均匀r命中128个根时返回同固定abort；因而`δ_FL,abort=0`。

单世界native隐私损失为

```
b_N = clip((N² + N(2Q4 + 2Q3 + 2Q6 + 4Q7
                       + Q5 + Q1 + Q2)) / W).
```

这里用源码usage编号。Q含内部调用，所以fresh seed重复/预查已被相应编程冲突覆盖；晚于公开的已知seed查询读原表。此界不假设恶意role诚实，不含FLP soundness。

拒绝采样按完整raw流和offset缓存。每个fresh隐藏field流需L个接受值，取搜索前缀`C_acc=L+128`、实际buffer预算`C_raw=32 ceil(C_acc/32)`，则严格模拟器的截断费用为

`Tail(L,C_acc)=Σ_(j=0)^(L−1) binom(C_acc,j)(q/W)^j ρ^(C_acc−j)`。

每report最多五条fresh流，L分别不超过10001、455、2、200、1。未prepare的report也可按五条保守收费。可取完全显式的

`t_N=clip(5N binom(10129,129) ρ^129)`。             (T)

因为在C_acc个候选内未取够L个接受值，至少129个拒绝；对这些拒绝位置做并集界即得。buffer最多额外31个prefetch字节块计入C_raw/T/bytes，不另生概率。重复流沿用同候选，无需再付独立tail；实际物理重展开仍计调用/bytes。总调用满足

`Q_int≤7N+4C_init,L+6C_init,R+C_msg,L+C_msg,R+C_finish,R`，

四种计数（descriptor、物理调用、接受值、raw bytes）不混用。本定理选择strict版本而加t_N；不一边声称严格时间一边略去无限几何循环。

### 3.1 公开96bit key tag：信息界与普通SHA单向性归约

实际setup发布`vdaf_key_tag=prefix96(SHA256(K))`，K为单task事前均匀16B verification key。未直接发布K不等于它在view条件下仍有128bit信息熵，因此原来的`2Q/W` key-guess项不成立。这个修正保留在本轮发现记录中，不改写早期预算输出。

首先不增加SHA假设：对任一96bit tag分支，first-hit之前的其它RO答案可用隐藏key-handle模拟；该分支至多G5_ext个候选。对最多2^96个tag分支求并，得

`k_info=clip(2^96 G5_ext/W)=clip(G5_ext/2^32)`。

这是平均命中率上界，无需假设tag均衡或从CR推出保密。它可能很松甚至饱和；不能据此称整个实例达到128bit完整性。

可另使用一个**明确新增的普通primitive单向性前提**：`Adv_SHA256^OW128(T_ow,Q_ow,B_ow)`的游戏取均匀`K←{0,1}^128`，给完整`h=SHA256(K)`，敌手输出任意16B的k使`SHA256(k)=h`。它是随机128bit输入域的preimage游戏，不是只寻找同96bit前缀，也不是目标native隐私/完整性假设。该性质不由SHA collision resistance自动推出。

归约取得h，只给底层敌手prefix96(h)，用它构造所有tag/config/body。诚实内部U5(K,nonce)按私有handle/nonce/offset在同表惰性取值，未知K也能模拟；其余usage和独立keys照常运行。每个**外部**U5候选k先算完整SHA256(k)：若等h，立即输出k赢OW，即使它是另一preimage也合法赢；否则可断定k≠K，按普通外部RO表回答。first true-key query必已让归约赢，之前联合view精确。扫描全部候选无需猜哪个索引，因此没有再乘G5_ext的损失。该归约要求K的C可见依赖只有公开tag及U5；私有admin配置/role DB不授予C，源码对应及相关假设由03专门核验。

资源为`Q_ow≤Q_sha+G5_ext`、`B_ow≤B_sha+16G5_ext`，T_ow包含整个wrapper/原生模拟、每候选full hash检查及表维护。单task单K无需猜目标key。两种独立证明的上界可取最小，定义

`k_tag=min(k_info,Adv_SHA256^OW128(T_ow,Q_sha+G5_ext,B_sha+16G5_ext))`。

不采用额外OW前提时就取k_tag=k_info；不得将未实例化的OW优势擅自填零，也不假装该新前提已经过文件测试认证。

### 3.2 C validity及诚实失败

原生verify key正确随机，C只见上述tag和允许接口而不见K本身。令P_att含所有不同首次攻击input，Q含全部离线grinding，03中两处key替换分别使用同上界k_tag，则

`v_N=clip((Q+P_att)·10256/q + 2k_tag + (2P_att+Q)²/W)`。 (V)

10256/q由非法输入多项式的10002/q加错误gadget polynomial的254/q得到；其余是03修订robustness的两个key替换和joint seed birthday/grinding。one proof不平方此值。若只用外生总Q代入信息界，可取更松的`2Q/2^32`并整体clip；该分支的算例可能很弱，明确展示而不以PASS掩盖。OW条件分支保留实际primitive优势，可提供更有用的条件界；两者都不声称无条件的128bit系统安全。P/P+A腐化role知道key，隐私猜的是诚实报告的未公布nonce，原b_N的Q5/W保持不变；不能拿(V)强制其non-H输出符合声明。

**诚实root失败。** 条件于fresh正确native随机性，N_h,p不同诚实prepare报告的root-abort概率至多`clip(128N_h,p/q)`，两role同r不是两个独立事件。公开RO预查等已按相应游戏单列。这是诚实执行失败/可用性账号，不是隐私损失，且不承诺网络或恶意永久拒绝下完成。Groth16 affine拒绝另由g_aff描述。没有把这些失败当成错误接纳，也没有条件化删掉真实abort。

## 4. C：声明完整性与全部前缀的定理

在01的C实验和02–06全部明确前提下，存在上述primitive归约，使

`ε_C ≤ clip(B_C + v_N)`。                         (C)

证明：在不发生B_C/v_N的任意prefix上，02为每个新来源提供合法R1CS assignment；H是固定合法honest source，恶意owner自己的签名不是知识。规范STATE message小于ℓ，同承诺的另一个规范坐标会形成binding双开口；整数约束范围均小于p，故字段等式提升为实际ADWC整数关系。05逐事件归纳保持真实head/K、quota和L依赖闭合。native两正确输出由(V)在合法一热域，receipt只从同retained输出计算，moment在该域单射，故其索引等于认证声明。每个诚实出口的持久reservation/bound payload要求完整P/R/L/M及retained关联，失败/重启不回滚暴露；因此首曝也对应固定完整R。

成功batch的逐报告计数在写Pg前转成i64；成功状态`report_count≤2^63−1<q`，各桶也是非负不超过该数，所以成功Decoder给精确整数histogram，不只是F_q模q结果。该界来自选定source，未来扩大count格式须重证。原子持久存储、正确服务和编译器/ISA不是由(C)概率认证的事实；条件失败时此定理不适用。永久拒绝、掉盘或主动role伪造最终share不在C的成功正确性保证内。

## 5. A、P及P+A：全view在线隐私定理

每个X∈{A,P,P+A}使用04实际在线模拟器，A没有aggregate接口；P/P+A只在完整R允许首曝时查询O_C，H/non-H的实际诚实aggregate严格为

`O_C(R)−Σ_(j∈R\H)e_(x_j)−Σ_(i∈R∩H)v_c,i^orig+Σ_(j∈R\H)w_h,j`。

定义隐藏challenge ciphertext预算`C_A=4N+E_enc,A`、`C_P=C_(P+A)=2N`。每份新HPKE封装都计一个hop；字节缓存不新增，重加密须新增。按实际recipient key列出这些challenge，令

`H_X=Σ_(j=1)^C_X Adv_HPKE,k(j)^IND-CCA2(T_red,j,1,D_hpke[k(j)],L_hpke[j])`。

优势定义为两个challenge分布的输出bit概率gap，最多1；这是single-shot Base suite X25519/HKDF-SHA256/AES-128-GCM、完整info/AAD标签且精确challenge tuple禁解密的primitive游戏。04给同tuple只走唯一授权H/source handle的origin/上下文论证；不同AAD/RID/key/info/ciphertext用合法decrypt oracle返回真实plaintext或bottom，不能一律假拒绝。需要加密随机性的所有内部工作与解密bytes均入该单challenge资源。多key多challenge通过上述逐项和，而非一句未给参数的“HPKE安全”。

为保守计入不同hybrid中可发生的路由坏事件，除`C_X`个cipher hops，按顺序列十个宏hop：①sourceproof采样；②native nonce去重；③初始RO编程；④measurement/proof shares与parts编程；⑤移除未知prover coins；⑥FLP full-verifier替换；⑦隐藏point/receipt联合变换；⑧raw candidate trace耦合；⑨业务/完整R首曝后处理；⑩strict-PPT截断。03中的每个有损native子hop在此都有独立端点，不能因b_N已经求和就省掉其路由端点。root-abort、固定长度及业务后处理在good domain上精确；raw trace在截断前也是精确联合耦合。对每相邻hop的两端分别去掉坏事件至多2B_X，故总端点数可用

`M_X=2(C_X+10)`。

对该固定世界，逐hybrid三角不等式给

`Δ_X(b) ≤ e_X=clip(M_X B_X + H_X + b_N + t_N)`。     (P1)

这里identity/affine已纳入每端B_X，不再额外假设只发生一次的master coupling。SHA在每端仍只有一个全调用账号；乘端点数是互斥实验的并集上界，不是把SHA变成独立随机函数。primitive/G16/S caps应覆盖每个端点；若某端点实际用更少，使用共同上界仍合法。

两个合法世界有相同μ；对P/P+A还在每个获准完整R有相同O_C，而A无需等和。最终S只用这些接口、独立coins、已知敌手动作和自己的状态，因此是同一个分布。于是

`Adv_X^two-world ≤ clip(e_X(0)+e_X(1)) ≤ clip(2e_X)`， (P2)

其中最后一步用两世界共同资源上界。单世界real/ideal距离和两世界gap不混用；δ_FL用L1但为0，未引入二分之一约定错误。

**联合view与时序的理由。** 04同时采样承诺、sourceproof、ciphertext及native verifier/receipt。P的真实恒等式`m_h=T−F(v_c^orig)−r_c`使恶意peer新增moment verdict只检查它自己原始份额；A的`(T,m_0,m_1)=(U,V,U−V)`精确且无aggregate。commit/abort/error、DB/WAL/backup与公开编码长度从同一模拟业务状态生成；不能把真实secret verdict/time预先给S。03将raw拒绝轨迹附加在同RO表，05保留事务回滚、exact journal与持久send顺序，标准executor中实际timeout是模拟工作和外生调度的因果后处理。因此该归纳覆盖每个prefix及首曝后collection失败，不仅最终SUCCESS。input-ready之前的本地prover时间、物理侧信道和任意硬件不由此推导。

## 6. 可计算账本、负控制和适用范围

[机器预算合同](composition-budget-contract.json)逐项列出上式，计算使用整数和精确Fraction，不用浮点声称安全级别。检查器 [source omitted from this derivative]核对两个专项合同常量、边界/单调性、三个key、端点数、四种资源及反例；其数值示例只展示符号界，不把primitive Adv置零后冒充整个系统安全，也不是测得的攻击者预算或参数推荐。没有通过有限算例验证密码学假设或完整无界证明。

G4b全部通过的含义是本合同要求的完整数学论证、显式账本、源码精化和反例已完成并在这些精确文档/版本上通过内部独立审读与机械验收。数学未由proof assistant核验，开发setup未获生产认证；G3并行修复、G5 native、G6实验与G7入稿仍按各自Gate签收。冻结G4a保持历史文件不变，当前共享G3 test helper漂移的隔离理由见00/intake002；它不被当成本定理协议source。
