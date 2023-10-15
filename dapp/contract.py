from solcx import compile_files, install_solc

def compile_contract(contract_path):
    install_solc("0.8.21")
    compiled_sol = compile_files(
        [contract_path],
        output_values=["abi", "bin"],
        solc_version="0.8.21"
    )
    _, contract_interface = compiled_sol.popitem()
    bytecode = contract_interface['bin']
    abi = contract_interface['abi']
    return abi, bytecode
