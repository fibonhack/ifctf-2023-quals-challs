#!/usr/bin/env python3.10

import ast
from typing import Any

"""
Recursively ransform this:

(lambda f1: f1(expr1))(lambda x1:
    (lambda f2: f2(expr2))(lambda x2:
        [...]
    )
)

into this:

x1 = expr1
x2 = expr2
[...]

"""

def pp(node):
    print(ast.dump(node, indent=4))

class DeobfuscateTransformer(ast.NodeTransformer):
    def __init__(self):
        super().__init__()
        self.statements = []
    
    def visit_Module(self, node) -> Any:
        self.generic_visit(node)
        # return the statements
        node.body = self.statements
        return node
    
    def visit_Call(self, node):
        """
        We are interested in this pattern
        (lambda f1: f1(expr1))(lambda x1: something)

        We want to transform it into
        x1 = expr1
        and recurse on something
        """
        f = node.func

        if isinstance(f, ast.Lambda):
            # pp(node)
            identifier = f.args.args[0].arg
            # print(identifier)
            # pp(f.body)
            if isinstance(f.body, ast.Call):
                func_name = f.body.func.id
                if func_name == identifier:
                    # print('bind lambda')
                    expr = f.body.args[0]
                    bind_lambda = node.args[0]
                    bind_name = bind_lambda.args.args[0].arg
                    # print('bind', bind_name, 'to', ast.dump(expr))
                    self.statements.append(ast.Assign(
                        targets=[ast.Name(id=bind_name, ctx=ast.Store())],
                        value=expr
                    ))
                    # pp(bind_lambda)
                    self.visit(bind_lambda.body)
                    return node
        self.visit(node)
        return node

chall = """
(lambda _0: _0(37))(lambda _1: (lambda _2: _2(lambda _3: lambda _4: _3 == _4))(lambda _5: (lambda _6: _6(lambda _7: lambda _8: _7 + _8))(lambda _9: (lambda _10: _10(lambda _11: lambda _12: _11 % _12))(lambda _13: (lambda _14: _14(lambda _15: lambda _16: _15 * _16))(lambda _17: (lambda _18: _18(lambda _19: lambda _20: _19 ^ _20))(lambda _21: (lambda _22: _22(_13))(lambda _23: (lambda _24: _24(_17))(lambda _25: (lambda _26: _26(_1))(lambda _27: (lambda _28: _28(lambda _29: lambda _30: _23(_25(_29)(_30))(_27)))(lambda _31: (lambda _32: _32(_13))(lambda _33: (lambda _34: _34(_9))(lambda _35: (lambda _36: _36(_1))(lambda _37: (lambda _38: _38(lambda _39: lambda _40: _33(_35(_39)(_40))(_37)))(lambda _41: (lambda _42: _42(lambda _43: (lambda _44: _43(lambda _45: _44(_44)(_45)))(lambda _46: _43(lambda _47: _46(_46)(_47)))))(lambda _48: (lambda _49: _49(_5))(lambda _50: (lambda _51: _51(0))(lambda _52: (lambda _53: _53(_50(_52)))(lambda _54: (lambda _55: _55(1))(lambda _56: (lambda _57: _57(_17))(lambda _58: (lambda _59: _59(_9))(lambda _60: (lambda _61: _61(-1))(lambda _62: (lambda _63: _63(_60(_62)))(lambda _64: (lambda _65: _65(lambda _66: lambda _67: _56 if _54(_67) else _58(_67)(_66(_64(_67)))))(lambda _68: (lambda _69: _69(_5))(lambda _70: (lambda _71: _71(0))(lambda _72: (lambda _73: _73(_70(_72)))(lambda _74: (lambda _75: _75([]))(lambda _76: (lambda _77: _77(_9))(lambda _78: (lambda _79: _79(_41))(lambda _80: (lambda _81: _81(_31))(lambda _82: (lambda _83: _83(_48))(lambda _84: (lambda _85: _85(_68))(lambda _86: (lambda _87: _87(_84(_86)))(lambda _88: (lambda _89: _89(4))(lambda _90: (lambda _91: _91(_88(_90)))(lambda _92: (lambda _93: _93(_82(_92)))(lambda _94: (lambda _95: _95(lambda _96: lambda _97: _76 if _74(_97) else _78(_96(_97 - 1))([_80(_97)(_94(_97))])))(lambda _98: (lambda _99: _99(_5))(lambda _100: (lambda _101: _101(0))(lambda _102: (lambda _103: _103(_100(_102)))(lambda _104: (lambda _105: _105(len))(lambda _106: (lambda _107: _107([]))(lambda _108: (lambda _109: _109(_9))(lambda _110: (lambda _111: _111(lambda _112: lambda _113: lambda _114: _108 if _104(_106(_114)) else _110(_112(_113)(_114[1:]))([_113[_114[0]]])))(lambda _115: (lambda _116: _116(_5))(lambda _117: (lambda _118: _118(0))(lambda _119: (lambda _120: _120(_117(_119)))(lambda _121: (lambda _122: _122(len))(lambda _123: (lambda _124: _124([]))(lambda _125: (lambda _126: _126(_9))(lambda _127: (lambda _128: _128(lambda _129: lambda _130: lambda _131: _125 if _121(_123(_131)) else _127([_130(_131[0])])(_129(_130)(_131[1:]))))(lambda _132: (lambda _133: _133(_5))(lambda _134: (lambda _135: _135(0))(lambda _136: (lambda _137: _137(_134(_136)))(lambda _138: (lambda _139: _139(len))(lambda _140: (lambda _141: _141([]))(lambda _142: (lambda _143: _143(_9))(lambda _144: (lambda _145: _145(lambda _146: lambda _147: lambda _148: _142 if _138(_140(_148)) else _144([_148[:_147]])(_146(_147)(_148[_147:]))))(lambda _149: (lambda _150: _150(lambda _151: lambda _152: _151 + _17('X')(_13(_9(_152)(-len(_151)))(_152))))(lambda _153: (lambda _154: _154(_5))(lambda _155: (lambda _156: _156(0))(lambda _157: (lambda _158: _158(_155(_157)))(lambda _159: (lambda _160: _160(len))(lambda _161: (lambda _162: _162(0))(lambda _163: (lambda _164: _164(_9))(lambda _165: (lambda _166: _166(ord))(lambda _167: (lambda _168: _168(_17))(lambda _169: (lambda _170: _170(256))(lambda _171: (lambda _172: _172(_169(_171)))(lambda _173: (lambda _174: _174(lambda _175: lambda _176: _163 if _159(_161(_176)) else _165(_167(_176[0]))(_173(_175(_176[1:])))))(lambda _177: (lambda _178: _178(print))(lambda _179: (lambda _180: _180('Give me the flag...'))(lambda _181: (lambda _182: _182(_179(_181)))(lambda _183: (lambda _184: _184(input))(lambda _185: (lambda _186: _186('λ >'))(lambda _187: (lambda _188: _188(_185(_187)))(lambda _189: (lambda _190: _190(_48))(lambda _191: (lambda _192: _192(_115))(lambda _193: (lambda _194: _194(_191(_193)))(lambda _195: (lambda _196: _196(_189))(lambda _197: (lambda _198: _198(_195(_197)))(lambda _199: (lambda _200: _200(_48))(lambda _201: (lambda _202: _202(_98))(lambda _203: (lambda _204: _204(_201(_203)))(lambda _205: (lambda _206: _206(_1))(lambda _207: (lambda _208: _208(_205(_207)))(lambda _209: (lambda _210: _210(_199(_209)))(lambda _211: (lambda _212: _212(''.join))(lambda _213: (lambda _214: _214(_211))(lambda _215: (lambda _216: _216(_213(_215)))(lambda _217: (lambda _218: _218(_153))(lambda _219: (lambda _220: _220(_217))(lambda _221: (lambda _222: _222(_219(_221)))(lambda _223: (lambda _224: _224(5))(lambda _225: (lambda _226: _226(_223(_225)))(lambda _227: (lambda _228: _228(_48))(lambda _229: (lambda _230: _230(_149))(lambda _231: (lambda _232: _232(_229(_231)))(lambda _233: (lambda _234: _234(5))(lambda _235: (lambda _236: _236(_233(_235)))(lambda _237: (lambda _238: _238(_227))(lambda _239: (lambda _240: _240(_237(_239)))(lambda _241: (lambda _242: _242(_21))(lambda _243: (lambda _244: _244(_17))(lambda _245: (lambda _246: _246(3405691582))(lambda _247: (lambda _248: _248(_245(_247)))(lambda _249: (lambda _250: _250(42))(lambda _251: (lambda _252: _252(_249(_251)))(lambda _253: (lambda _254: _254(_243(_253)))(lambda _255: (lambda _256: _256(_48))(lambda _257: (lambda _258: _258(_132))(lambda _259: (lambda _260: _260(_257(_259)))(lambda _261: (lambda _262: _262(_48))(lambda _263: (lambda _264: _264(_177))(lambda _265: (lambda _266: _266(_263(_265)))(lambda _267: (lambda _268: _268(_261(_267)))(lambda _269: (lambda _270: _270(_241))(lambda _271: (lambda _272: _272(_269(_271)))(lambda _273: (lambda _274: _274(_48))(lambda _275: (lambda _276: _276(_132))(lambda _277: (lambda _278: _278(_275(_277)))(lambda _279: (lambda _280: _280(_255))(lambda _281: (lambda _282: _282(_279(_281)))(lambda _283: (lambda _284: _284(_273))(lambda _285: (lambda _286: _286(_283(_285)))(lambda _287: (lambda _288: _288([]))(lambda _289: (lambda _290: _290(_289.append))(lambda _291: (lambda _292: _292(541982718533))(lambda _293: (lambda _294: _294(_291(_293)))(lambda _295: (lambda _296: _296(_289.append))(lambda _297: (lambda _298: _298(541752425566))(lambda _299: (lambda _300: _300(_297(_299)))(lambda _301: (lambda _302: _302(_289.append))(lambda _303: (lambda _304: _304(541920185944))(lambda _305: (lambda _306: _306(_303(_305)))(lambda _307: (lambda _308: _308(_289.append))(lambda _309: (lambda _310: _310(507556842335))(lambda _311: (lambda _312: _312(_309(_311)))(lambda _313: (lambda _314: _314(_289.append))(lambda _315: (lambda _316: _316(288517769026))(lambda _317: (lambda _318: _318(_315(_317)))(lambda _319: (lambda _320: _320(_289.append))(lambda _321: (lambda _322: _322(542133179466))(lambda _323: (lambda _324: _324(_321(_323)))(lambda _325: (lambda _326: _326(_289.append))(lambda _327: (lambda _328: _328(305508892749))(lambda _329: (lambda _330: _330(_327(_329)))(lambda _331: (lambda _332: _332(_289.append))(lambda _333: (lambda _334: _334(520052997187))(lambda _335: (lambda _336: _336(_333(_335)))(lambda _337: (lambda _338: _338(print))(lambda _339: (lambda _340: _340(_5))(lambda _341: (lambda _342: _342(_289))(lambda _343: (lambda _344: _344(_341(_343)))(lambda _345: (lambda _346: _346(_287))(lambda _347: (lambda _348: _348(_345(_347)))(lambda _349: (lambda _350: _350("That's it!"))(lambda _351: (lambda _352: _352('Nope!'))(lambda _353: (lambda _354: _354(_339(_351 if _349 else _353)))(lambda _355: lambda _356: _356))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))))
"""

parsed = ast.parse(chall)
parsed = DeobfuscateTransformer().visit(parsed)

parsed = ast.fix_missing_locations(parsed)

script = f"{ast.unparse(parsed)}"
print(script)

