import logging
from pathlib import Path

import boa

from scripts.deploy.constants import ETHEREUM_ADMINS
from scripts.deploy.utils import deploy_contract
from settings.config import BASE_DIR, RollupType

logger = logging.getLogger(__name__)


BROADCASTERS = {
    RollupType.op_stack: "",
    RollupType.polygon_cdk: "0xB5e7fE8eA8ECbd33504485756fCabB5f5D29C051",
    RollupType.arb_orbit: "",
}


def deploy_xgov(chain: str, rollup_type: RollupType):
    agent_blueprint = deploy_contract(chain, Path(BASE_DIR, "contracts", "governance", "agent"), as_blueprint=True)

    match rollup_type:
        case RollupType.op_stack:
            r_args = ("0x4200000000000000000000000000000000000007",)  # messenger
        case RollupType.polygon_cdk:
            r_args = (
                "0x2a3DD3EB832aF982ec71669E178424b10Dca2EDe",  # bridge
                0,  # origin network
            )
        case RollupType.arb_orbit:
            r_args = ("0x000000000000000000000000000000000000064",)  # arbsys
        case _:
            raise NotImplementedError("zksync currently not supported")

    relayer = deploy_contract(
        chain, Path(BASE_DIR, "contracts", "governance", chain, "relayer"), BROADCASTERS[rollup_type], agent_blueprint, *r_args
    )

    return relayer.OWNERSHIP_AGENT(), relayer.PARAMETER_AGENT(), relayer.EMERGENCY_AGENT()


def deploy_dao_vault(chain: str, owner: str):
    return deploy_contract(chain, Path(BASE_DIR, "contracts", "governance", "vault"), owner)
