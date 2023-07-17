from pathlib import Path
from beaker import *
from pyteal import *
from utils import build

app = Application("HelloWorld")

handle_creation = Seq(
    App.globalPut(Bytes("Slot"), Int(0)),
    Approve()
)

# Router is the command center
# Handles routing for incoming application calls
router = Router(
    "simple slot",
    BareCallActions(
        no_op=OnCompleteAction.create_only(handle_creation),
    ),
)

@app.external
def hello(name: abi.String, *, output: abi.String) -> Expr:
    return output.set(Concat(Bytes("Hello, "), name.get()))

@app.delete(bare=True, authorize=Authorize.only(Global.creator_address()))
def delete() -> Expr:
    return Approve()

@router.method
def slot():
    scratchCount = ScratchVar(TealType.uint64)
    return Seq(
        scratchCount.store(App.globalGet(Bytes("Slot"))),
        App.globalPut(Bytes("Slot"), scratchCount.load() +Int(1)),
    )

@router.method
def read_count(*, output:abi.Uint64):
    return output.set(App.globalGet(Bytes("Slot")))

if __name__ == "__main__":
    root_path = Path(__file__).parent
    build(root_path / "artifacts", app)
