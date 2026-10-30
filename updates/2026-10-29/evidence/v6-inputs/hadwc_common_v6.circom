pragma circom 2.1.9;
include "circomlib/circuits/bitify.circom";
include "circomlib/circuits/comparators.circom";
include "circomlib/circuits/babyjub.circom";
include "circomlib/circuits/escalarmulfix.circom";
// Generated v5 constants from public SHA256 labels; no v3/v4 pair reuse.
function G_STATE() { return [19840739292621837485429407101284405011723526012908037861472791205328010337531, 18778593471010398727627405732863822524826996614258619174338485809053874497281]; }
function H_STATE() { return [177934572111867414519459053939752309243371210765801809700074027242144501757, 9572740385273229743735740705230653405441189570988550994445020698489117537450]; }
function G_MASK_A() { return [4961400296463487211282937973076428162957196026316301460945623393972185147386, 16649654910185046506746527476424982869916709813549703890766661537556786385143]; }
function H_MASK_A() { return [5115020646149412395144980207094275296681497926501397038630931152666662308136, 13536267154676265594905092411367710185617455991420431575493161008080755812365]; }
function G_MASK_R() { return [16016734568363863576121299863329432047024911997196995900918690146465885293281, 4623395874020267920800102496796325379630100917730755177180265910238843298453]; }
function H_MASK_R() { return [8278456821456840947079912903776418089636062050941490858610100170101312672139, 2193498567714523101750039843347096570872273293985567911937515155191407955431]; }
function G_TICKET() { return [13295737051783157518344307231888327063707510706167971803496062388451026585357, 397772712171602258926972359663705995258280096146789412053675038089810662097]; }
function H_TICKET() { return [11923630485660139244507669525371405924167262172413057233804518314299231203739, 3441920207925543106907818820227194157818096894319552034389789670953014171779]; }
function G_RECEIPT() { return [16032246650595460846768982770014367027099404649917972481289107968035674563761, 13523710949613133126862443011813671342768306384753467244277873164504587534937]; }
function H_RECEIPT() { return [7658307965130273110887527337784708773565581674536020864727470403492569490580, 6648230921521704344330218114634145492044536601883688820203308248730155871956]; }
template Bounded(n, maximum) {
    signal input in;
    component bits = Num2Bits(n); bits.in <== in;
    component bound = LessEqThan(n);
    bound.in[0] <== in; bound.in[1] <== maximum; bound.out === 1;
}
template State() {
    signal input cell[2]; signal input rem[2]; signal input xy[2];
    signal output message;
    component c[2]; component r[2]; component x[2];
    for (var i=0; i<2; i++) {
        c[i] = Bounded(7,99); c[i].in <== cell[i];
        r[i] = Bounded(7,99); r[i].in <== rem[i];
        x[i] = Bounded(14,9999); x[i].in <== xy[i];
        xy[i] === cell[i]*100 + rem[i];
    }
    message <== xy[0]*1048576 + xy[1];
}
template Commit(n, G, H) {
    signal input message; signal input rho; signal output point[2];
    component mb = Num2Bits(n); mb.in <== message;
    component rb = Bounded(251,2736030358979909402780800718157159386076813972158567259200215660948447373040);
    rb.in <== rho;
    component rbits = Num2Bits(251); rbits.in <== rho;
    component gm = EscalarMulFix(n,G); component hm = EscalarMulFix(251,H);
    for (var i=0;i<n;i++) gm.e[i] <== mb.out[i];
    for (var i=0;i<251;i++) hm.e[i] <== rbits.out[i];
    component sum = BabyAdd();
    sum.x1 <== gm.out[0]; sum.y1 <== gm.out[1];
    sum.x2 <== hm.out[0]; sum.y2 <== hm.out[1];
    point[0] <== sum.xout; point[1] <== sum.yout;
}
template Distance(cap) {
    signal input current[2]; signal input reference[2];
    signal delta[2]; signal biased[2]; signal square[2];
    component ranges[2]; component squares[2];
    for(var i=0;i<2;i++) {
        delta[i] <== current[i]-reference[i];
        biased[i] <== delta[i]+9999;
        ranges[i] = Bounded(15,19998); ranges[i].in <== biased[i];
        square[i] <== delta[i]*delta[i];
        squares[i] = Bounded(27,99980001); squares[i].in <== square[i];
    }
    signal total <== square[0]+square[1];
    component maxTotal = Bounded(28,199960002); maxTotal.in <== total;
    component policy = Bounded(28,cap); policy.in <== total;
}
