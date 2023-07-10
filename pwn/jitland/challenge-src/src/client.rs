extern crate solana_rbpf;
use std::borrow::BorrowMut;

use hex;
use pwn::{self, context, Tube};
use solana_rbpf::{
    aligned_memory::AlignedMemory,
    assembler::assemble,
    ebpf,
    elf::Executable,
    memory_region::{MemoryMapping, MemoryRegion},
    verifier::{RequisiteVerifier, TautologyVerifier, Verifier, VerifierError},
    vm::{BuiltInProgram, Config, EbpfVm, FunctionRegistry, TestContextObject},
};
use std::io::{self, Read};

const SHOULD_JITCOMPILE: bool = true;

fn struct_to_blob<T>(input: T) -> Vec<u8> {
    let size = std::mem::size_of::<T>();
    let input_bytes: &[u8] = unsafe {
        let raw_ptr: *const u8 = std::mem::transmute(&input);
        std::slice::from_raw_parts(raw_ptr, size)
    };
    input_bytes.to_vec()
}

fn main() {
    // read from stdin until it is closed
    let mut input = String::new();
    let mut handle = io::stdin().lock();
    handle.read_to_string(&mut input);
    //handle.read_to_string(&mut input);

    // 0x00007ffe58cd8000-7ffe58cf9000
    let executable = assemble::<TestContextObject>(
        &input,
        std::sync::Arc::new(BuiltInProgram::new_loader(Config {
            ..Default::default()
        })),
    )
    .unwrap();

    let prog = executable.get_text_bytes().1;
    let mem = &mut [0xaa, 0xbb, 0x11, 0x22, 0xcc, 0xdd];
    let config = Config {
        enable_instruction_tracing: false,
        enable_instruction_meter: false,
        enable_address_translation: false,
        ..Default::default()
    };
    let config_blob = struct_to_blob(config);

    let prog_hex = hex::encode(prog);
    let mem_hex = hex::encode(mem);
    let config_hex = hex::encode(config_blob);
    println!("prog_hex: {}", prog_hex);
    println!("mem_hex: {}", mem_hex);
    println!("config_hex: {}", config_hex);

    /*/
    // let mut io = pwn::Remote::new("localhost", 10015).unwrap();
    let mut io = pwn::process::Process::new("./server").unwrap();
    //io.interactive().unwrap();
    io.recvuntil("Enter your program as a hex string: ".as_bytes())
        .unwrap();
    io.sendline(prog_hex.as_str()).unwrap();
    io.recvuntil("Enter your program memory as a hex string: ".as_bytes())
        .unwrap();
    io.sendline(mem_hex.as_str()).unwrap();
    io.recvuntil("Enter your program config as a hex string: ".as_bytes())
        .unwrap();
    io.sendline(config_hex.as_str()).unwrap();
    io.interactive().unwrap();
    */
}
