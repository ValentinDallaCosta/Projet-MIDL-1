# Syntax definition of formulas 

from dataclasses import dataclass
from collections.abc import Callable

# Comparison operators
class ComparOp:
    pass

@dataclass(frozen=True)
class Eq(ComparOp):
    def __str__(self):
        return "="

@dataclass(frozen=True)
class Lt(ComparOp):
    def __str__(self):
        return "<"


# Boolean operators
class BoolOp:
    pass

@dataclass(frozen=True)
class Conj(BoolOp):
    def __str__(self):
        return "∧"

@dataclass(frozen=True)
class Disj(BoolOp):
    def __str__(self):
        return "∨"


# Quantifiers
class Quantif:
    pass

@dataclass(frozen=True)
class All(Quantif):
    def __str__(self):
        return "∀"

@dataclass(frozen=True)
class Ex(Quantif):
    def __str__(self):
        return "∃"

# Formulas

class Formula:
    pass

@dataclass(frozen=True)
class ConstF(Formula):
    val: bool
    def __str__(self):
        if self.val:
            return "⊤"
        else:
            return "⊥"

# Variable (atomic proposition or predicate variable)
@dataclass(frozen=True)
class ComparF(Formula):
    left: str
    op: ComparOp
    right: str
    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

# Logical connectives
@dataclass(frozen=True)
class NotF(Formula):
    sub: Formula
    def __str__(self):
        return f"¬({self.sub})"

@dataclass(frozen=True)
class BoolOpF(Formula):
    left: Formula
    op: BoolOp
    right: Formula
    def __str__(self):
        return f"({self.left} {self.op} {self.right})"

@dataclass(frozen=True)
class QuantifF(Formula):
    q: Quantif
    var: str
    body: Formula
    def __str__(self):
        return f"{self.q}{self.var}.({self.body})"

# Some abbreviations
def eqf(x:str, y:str) -> ComparF:
    return(ComparF(x, Eq(), y))

def ltf(x:str, y:str) -> ComparF:
    return(ComparF(x, Lt(), y))

def conj(x:Formula, y:Formula) -> Formula:
    return(BoolOpF(x, Conj(), y))

def disj(x:Formula, y:Formula) -> Formula:
    return(BoolOpF(x, Disj(), y))

def impl(x: Formula, y: Formula):
    return(disj(NotF(x), y))

# cannot simply be called "all" because of Python keywords
def allq(v: str, f:Formula) -> Formula:
    return(QuantifF(All(), v, f))

def exq(v: str, f:Formula) -> Formula:
    return(QuantifF(Ex(), v, f))
