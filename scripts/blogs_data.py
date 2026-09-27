"""
blogs_data.py - Enterprise Mainframe Knowledge Base Article Definitions
Authored for StackMF Technologies LLP (stackmf.com)
25 Comprehensive, Production-Grade Mainframe Deep Dives covering:
COBOL, DB2, CICS, VSAM, IMS DB/DC, TELON, REXX, ENDEVOR, CHANGEMAN, CA-7,
ABENDs, Modernisation, DB2 SQL Tuning, and Performance Optimization.
"""

ARTICLES = [
    # -------------------------------------------------------------------------
    # 1. SOC7 DATA EXCEPTION IN COBOL PACKED DECIMAL
    # -------------------------------------------------------------------------
    {
        "slug": "soc7-data-exception-cobol-packed-decimal",
        "title": "Resolving ABEND S0C7 (Data Exception) in COBOL Packed-Decimal (COMP-3) Fields",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["COBOL", "z/OS", "S0C7", "COMP-3", "CEEDUMP", "Batch"],
        "reading_time": "9 min read",
        "tldr": "ABEND S0C7 occurs when an arithmetic statement or NUMERIC test encounters invalid packed-decimal data (such as uninitialized spaces X'4040' or low-values X'0000') in a COMP-3 field without a valid nibble sign (C, D, or F). Fix it using INITIALIZE, defensive NUMERIC checks, and proper compiler options.",
        "problem": """During high-volume batch billing or financial reconciliation runs on IBM z/OS, batch job steps fail abruptly with:
```text
SYSTEM COMPLETION CODE=0C7  REASON CODE=00000007
PSW AT TIME OF INTERRUPT: 078D1000 84A3B214  ILC 6  INTC 07
CEE3207S The system was unable to complete execution due to a data exception.
         From compile unit ACCNTREC at entry point PROCESS-INVOICE at statement 842.
```
Developers inspect the job log and find that statement 842 (`COMPUTE WS-TOTAL-BALANCE = WS-TOTAL-BALANCE + WS-INVOICE-AMT`) caused the crash. The batch stream halts mid-cycle, leaving datasets half-updated and downstream CA-7 dependencies blocked.""",
        "root_cause": """Packed decimal (`COMP-3` or `USAGE COMPUTATIONAL-3`) stores two decimal digits per byte, with the lowest nibble of the rightmost byte containing the sign:
- Valid positive sign nibbles: `X'C'` or `X'F'` (e.g., `+125` is stored as `X'125C'` or `X'125F'`)
- Valid negative sign nibbles: `X'D'` (e.g., `-125` is stored as `X'125D'`)

When a record is read from a sequential file (QSAM), VSAM, or MQ payload where the sender populated the field with EBCDIC spaces (`X'40'`), binary zeroes (`X'00'`), or corrupted alphanumeric characters, the System/390 / z/Architecture hardware execution unit runs an `AP` (Add Packed), `MP` (Multiply Packed), or `CP` (Compare Packed) instruction. The CPU hardware microcode validates each digit (`0-9`) and the terminating sign nibble. If any digit exceeds `9` or the sign is not `A-F` (specifically `C`, `D`, or `F`), the hardware raises an Interrupt Code 07 (Data Exception), translated by MVS into ABEND S0C7.""",
        "solution": """### 1. Identify the Exact Offending Field from CEEDUMP
Locate the compiler listing or examine the Language Environment CEEDUMP:
1. Search for `Traceback` in the CEEDUMP. Note the statement number (e.g., `Statement 842`).
2. Examine the `Parameters and Local Variables` section.
3. Look at the hexadecimal dump of the variables involved in the arithmetic operation:
   `WS-INVOICE-AMT: X'4040404040'` (pure spaces!) or `X'0000000000'` (uninitialized binary zeroes).

### 2. Implement Defensive Validation in COBOL
Do not perform direct arithmetic on external inputs without pre-clearing or testing:
```cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. ACCNTREC.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-INVOICE-RECORD.
           05  WS-RAW-AMOUNT-ALPHA      PIC X(07).
           05  WS-INVOICE-AMT           PIC S9(7)V99 COMP-3.
           05  WS-TOTAL-BALANCE         PIC S9(9)V99 COMP-3 VALUE +0.

       PROCEDURE DIVISION.
       PROCESS-INVOICE.
      * Validate before calculation to prevent S0C7
           IF WS-RAW-AMOUNT-ALPHA IS NUMERIC
               COMPUTE WS-INVOICE-AMT = FUNCTION NUMVAL(WS-RAW-AMOUNT-ALPHA)
               ADD WS-INVOICE-AMT TO WS-TOTAL-BALANCE
           ELSE
               PERFORM 9900-HANDLE-CORRUPT-INPUT
           END-IF.
```

### 3. Ensure Strict Variable Initialization
Always initialize Working-Storage groups before reading records:
```cobol
       INITIALIZE WS-INVOICE-RECORD
                  REPLACING NUMERIC DATA BY ZEROES
                            ALPHANUMERIC DATA BY SPACES.
```

### 4. Enterprise COBOL 6.x Compiler Flags
Compile with `INITCHECK` and `NUMCHECK(PACF,ZON)` during test phases:
```jcl
//COBSTEP EXEC PGM=IGYCRCTL,
//  PARM='OPT(2),ARCH(14),NUMPROC(PFD),NUMCHECK(PACF,ZON),INITCHECK'
```
`NUMCHECK` generates runtime code to verify zoned and packed decimal validity before each instruction, pinpointing corrupt fields immediately before they cause production hardware exceptions.""",
        "prevention": [
            "Never use group MOVEs to populate records containing COMP-3 child fields (e.g., `MOVE SPACES TO WS-CUSTOMER-RECORD`). Always use `INITIALIZE`.",
            "Use `NUMPROC(PFD)` only if you guarantee clean signs; otherwise use `NUMPROC(NOPFD)` to allow compiler sign fixing.",
            "When consuming data from Web APIs, MQ, or Kafka via z/OS Connect, ensure JSON nulls are mapped to zero values rather than uninitialized storage.",
            "Run DFSORT or ICETOOL `VERIFY` checks on incoming flat files prior to invoking COBOL batch programs."
        ],
        "references": [
            {"title": "IBM Enterprise COBOL for z/OS: Handling Data Exceptions", "url": "https://www.ibm.com/docs/en/cobol-zos/latest?topic=exceptions-handling-data-exceptions"},
            {"title": "IBM z/OS MVS System Codes: S0C7 Details", "url": "https://www.ibm.com/docs/en/zos/latest?topic=codes-0c7"},
            {"title": "StackMF Mainframe Application Maintenance (AMS) Solutions", "url": "https://stackmf.com/#maintenance-ams"}
        ]
    },

    # -------------------------------------------------------------------------
    # 2. SOC4 PROTECTION EXCEPTION IN COBOL LINKAGE SECTION & POINTERS
    # -------------------------------------------------------------------------
    {
        "slug": "soc4-protection-exception-linkage-pointer",
        "title": "Debugging ABEND S0C4 (Protection Exception) in COBOL Linkage Section & Pointers",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["COBOL", "z/OS", "S0C4", "Linkage Section", "Pointers", "CICS"],
        "reading_time": "10 min read",
        "tldr": "ABEND S0C4 (0C4) indicates a hardware storage protection violation caused by dereferencing a NULL pointer, exceeding table OCCURS subscript boundaries without bounds checking, or accessing unallocated Linkage Section items. Learn how to parse the PSW, TEA, and CEEDUMP to isolate the invalid memory address.",
        "problem": """A core CICS online transaction or batch subprogram terminates with ABEND S0C4:
```text
SYSTEM COMPLETION CODE=0C4  REASON CODE=00000010
PSW AT TIME OF INTERRUPT: 078D2000 80004128  ILC 4  INTC 10
TRANSLATION EXCEPTION ADDR (TEA): 00000000_00000004
CEE3204S The system detected a protection exception (System Completion Code=0C4).
         From compile unit MODSUB1 at entry point MODSUB1 at statement 312.
```
The developer sees Reason Code 10 (Segment translation or page translation fault) and a Translation Exception Address (TEA) pointing near `00000004`. The transaction fails for end-users with CICS abend code `ASRA`.""",
        "root_cause": """In z/Architecture virtual storage, each 4KB page is protected by storage keys and page table entries. An S0C4 occurs when:
1. **Linkage Section Address Misalignment**: A program defines items under `LINKAGE SECTION` (or CICS `DFHCOMMAREA`) but the caller did not pass the argument in `CALL 'MODSUB1' USING BY REFERENCE PARM-A`. COBOL assigns address zero (`NULL`) to the corresponding BLL (Base Locator for Linkage) cell. Accessing any field within that structure attempts to read address `00000000 + offset`, violating page 0 protection.
2. **Table Subscript Out-of-Bounds**: Subscript or index loops run wild past the allocated `OCCURS` range (e.g., accessing item 500 in an array sized for 50), stepping across the virtual storage boundary into an unallocated or foreign key page.
3. **Storage Key Mismatch**: In CICS with Transaction Isolation active, an application running in User Key (Key 9) attempts to modify CICS System Storage (Key 8).""",
        "solution": """### 1. Inspect the Translation Exception Address (TEA)
Check the `TEA` or the register used as base in the instruction:
- If `TEA` is `00000000_00000000` through `00000FFF`, it is a **NULL pointer dereference**. A Linkage Section parameter was accessed without being passed or allocated.
- If `TEA` is `7FFFFFFF` or negative, an uninitialized integer or binary counter was used as an array index.

### 2. Verify Parameter Counts & Parmlists
Ensure the calling program passes every expected parameter by reference:
```cobol
      * CALLING PROGRAM
       CALL 'MODSUB1' USING BY REFERENCE WS-HEADER-RECORD
                                         WS-ITEM-ARRAY
                                         WS-RETURN-STATUS.

      * CALLED PROGRAM (MODSUB1)
       LINKAGE SECTION.
       01  LS-HEADER-RECORD        PIC X(100).
       01  LS-ITEM-ARRAY           PIC X(5000).
       01  LS-RETURN-STATUS        PIC X(04).

       PROCEDURE DIVISION USING LS-HEADER-RECORD
                                LS-ITEM-ARRAY
                                LS-RETURN-STATUS.
```
If `MODSUB1` is called dynamically and optional parameters are permitted, use `ADDRESS OF` to verify pointer validity before dereferencing:
```cobol
       IF ADDRESS OF LS-RETURN-STATUS NOT = NULL
           MOVE 'OK00' TO LS-RETURN-STATUS
       END-IF.
```

### 3. Check CICS EIBCALEN Before Reading DFHCOMMAREA
In CICS, always compare `EIBCALEN` to the expected commarea length:
```cobol
       IF EIBCALEN < LENGTH OF DFHCOMMAREA
           EXEC CICS RETURN
                     ABCODE('LENG')
           END-EXEC
       END-IF.
```

### 4. Enable SSRANGE in Non-Production Compiles
Catch subscript overflows during integration testing:
```jcl
//COBSTEP EXEC PGM=IGYCRCTL,PARM='SSRANGE,OPT(0),TEST'
```
When `SSRANGE` is active, the compiler emits instructions that intercept bounds breaches, producing a clear descriptive LE error message instead of an unexpected hardware S0C4.""",
        "prevention": [
            "Always compile with `SSRANGE` in Dev/QA environments to detect indexing regressions.",
            "Verify `EIBCALEN` immediately upon entering any CICS transaction program.",
            "In Enterprise COBOL 6.x, check 64-bit memory addresses and ensure `LP(64)` pointer variables are not truncated into 32-bit registers.",
            "Avoid hardcoded subscript limits; use `FUNCTION RECORDING-MODE` or `DEPENDING ON` clauses with rigorous upper-bound validation."
        ],
        "references": [
            {"title": "IBM z/OS MVS System Codes: Completion Code 0C4", "url": "https://www.ibm.com/docs/en/zos/latest?topic=codes-0c4"},
            {"title": "IBM Enterprise COBOL for z/OS: Using the Linkage Section", "url": "https://www.ibm.com/docs/en/cobol-zos/latest?topic=program-linkage-section"},
            {"title": "StackMF Full-Stack Mainframe Engineering Pods", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },

    # -------------------------------------------------------------------------
    # 3. SB37, SD37, SE37 SPACE ABENDS IN JCL & DATASETS
    # -------------------------------------------------------------------------
    {
        "slug": "sb37-sd37-se37-space-abends-jcl",
        "title": "Mastering SB37, SD37, and SE37 Out-of-Space ABENDs in z/OS Sequential & PDS Datasets",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["JCL", "z/OS", "DFSMS", "Storage", "SB37", "SD37", "SE37", "IDCAMS"],
        "reading_time": "8 min read",
        "tldr": "Space ABENDs (SB37, SD37, SE37) crash critical overnight batch jobs when datasets exceed volume, extent, or catalog limits. Discover how to configure secondary allocations, RLSE, SMS Dataclasses, and Extended Format attributes to prevent volume exhaustion.",
        "problem": """A critical end-of-month batch consolidation fails at 02:45 AM with:
```text
IEC030I B37-04,IFG0554A,JOBEOM01,STEP040,SYSUT2,3420,VOL004,PROD.BILLING.MONTHLY.EXTRACT
IEF450I JOBEOM01 STEP040 - ABEND=SB37 U0000 REASON=00000004
```
Alternatively, variations such as `D37-04` (No space available on current volume to satisfy secondary allocation request) or `E37-04` (Dataset already allocated maximum allowable extents: 123 for non-extended sequential or 16 for standard PDS) bring the overnight batch processing pipeline to a dead halt.""",
        "root_cause": """IBM DFSMS manages disk space allocations in primary and secondary extents:
- **SB37**: End of volume reached, and no secondary allocation quantity was specified in the JCL `SPACE` parameter, or the system could not mount a new volume.
- **SD37**: A secondary extent was requested, but the current DASD volume does not have a contiguous chunk of tracks/cylinders large enough to satisfy the minimum request, and no additional candidate volumes exist in the SMS Storage Group.
- **SE37**: The dataset reached the physical architectural limit of extents (16 extents on a single volume for basic PDS; 123 extents across all volumes for standard sequential datasets) or ran out of directory blocks (`D37` on PDS directory).""",
        "solution": """### 1. Optimize the JCL SPACE Allocation
Ensure secondary allocations and release unused space upon job completion:
```jcl
//SYSUT2   DD DSN=PROD.BILLING.MONTHLY.EXTRACT,
//            DISP=(NEW,CATLG,DELETE),
//            SPACE=(CYL,(150,50),RLSE),
//            UNIT=SYSDA,
//            DCB=(RECFM=FB,LRECL=250,BLKSIZE=27750)
```
- Primary: `150` cylinders allocated immediately.
- Secondary: `50` cylinders allocated dynamically whenever the file expands.
- `RLSE`: Frees unwritten cylinders at `CLOSE`, preventing DASD wastage.

### 2. Bypass Extent Limits with SMS Extended Addressability (EA)
For multi-gigabyte or terabyte batch files, assign an SMS Data Class configured for Extended Format:
```jcl
//SYSUT2   DD DSN=PROD.BILLING.MONTHLY.EXTRACT,
//            DISP=(NEW,CATLG,DELETE),
//            DATACLAS=DCEARGE,
//            STORCLAS=SCBATCH,
//            SPACE=(CYL,(500,100),RLSE)
```
Extended format datasets support up to 255 extents per volume and multi-volume spanning up to 59 volumes, completely eliminating the 123-extent barrier.

### 3. Recovering a PDS Out of Directory Blocks (SD37 / SE37)
If a partitioned dataset (PDS) fails due to exhausted directory blocks, expand it using IDCAMS:
```jcl
//STEP1    EXEC PGM=IDCAMS
//SYSPRINT DD SYSOUT=*
//SYSIN    DD *
  ALTER PROD.COBOL.LOADLIB -
        SPACE(50 20) -
        DIRECTORY(150)
/*
```
Better yet, convert legacy PDS datasets to PDSE (`DSNTYPE=LIBRARY`), which features dynamic directory allocation and automatic member space reclamation without requiring periodic `COMPRESS`.""",
        "prevention": [
            "Convert all legacy PDS libraries to PDSE (`DSNTYPE=LIBRARY`) to prevent directory block exhaustion and eliminate compress jobs.",
            "Establish SMS Storage Group monitoring thresholds at 80% DASD utilization to prevent volume full conditions.",
            "Always specify a realistic secondary allocation in batch JCL rather than relying solely on large primary extents.",
            "Utilize DFSMS Space Management automated pooling or third-party automated space recovery utilities."
        ],
        "references": [
            {"title": "IBM DFSMS Using Data Sets: Managing Space Allocation", "url": "https://www.ibm.com/docs/en/zos/latest?topic=allocating-space-data-sets"},
            {"title": "IBM z/OS MVS System Codes: B37, D37, and E37", "url": "https://www.ibm.com/docs/en/zos/latest?topic=codes-b37"},
            {"title": "StackMF Mainframe Modernization & Storage Consulting", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },

    # -------------------------------------------------------------------------
    # 4. S0C1 OPERATION EXCEPTION IN CICS & BATCH
    # -------------------------------------------------------------------------
    {
        "slug": "s0c1-operation-exception-cics-load",
        "title": "Diagnosing ABEND S0C1 (Operation Exception) in CICS & Batch Execution",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["COBOL", "z/OS", "S0C1", "CICS", "Linkage Editor", "HLASM"],
        "reading_time": "7 min read",
        "tldr": "ABEND S0C1 occurs when the mainframe CPU attempts to execute an instruction with an invalid or undefined operation code. Common causes include calling an unlinked dummy subroutine, branching into Working-Storage data, or mismatched AMODE/RMODE compiler parameters.",
        "problem": """A newly compiled COBOL module deployed via Endevor or ChangeMan fails immediately upon invocation:
```text
SYSTEM COMPLETION CODE=0C1  REASON CODE=00000001
PSW AT TIME OF INTERRUPT: 078D1000 80000002  ILC 2  INTC 01
IEA995I SYMPTOM DUMP OUTPUT
  USER COMPLETION CODE=XXXX
  PSW AT ENTRY TO ABEND   078D1000  80000002
```
In CICS, the transaction abends with `ASRA`, and the execution address in the CICS dump points to an area populated with binary zeroes (`X'0000'`).""",
        "root_cause": """The z/Architecture hardware microcode inspects the first byte of every machine instruction to determine the operation code (opcode). An S0C1 (Interrupt Code 01) triggers when:
1. **Unresolved External Reference**: A COBOL program executes `CALL 'SUBPGM1'`, but during the Link-Edit / Binder phase, `SUBPGM1` was not in the `SYSLIB` concatenation. The Binder marked the entry point as unresolved or resolved it to address zero (`00000000`). When executed, the CPU jumps to address 0, encounters `X'0000'`, and abends with S0C1.
2. **Branching into Data**: An overwritten return address in the save area (due to a buffer overrun or corrupt register 14) causes the program to return into variable storage rather than executable code.
3. **AMODE Switching Fault**: Calling a 31-bit subprogram from a 24-bit caller without proper `AMODE 31` linkage or BASSM instruction.""",
        "solution": """### 1. Verify Linkage Editor / Binder Output
Inspect the Binder listing (`SYSPRINT`) from the compile/link job. Check for:
```text
IEW2456E 9207 SYMBOL SUBPGM1 UNRESOLVED.  MEMBER MARKED NOT EXECUTABLE.
```
If the Binder flag `NCAL` (No Call) was specified without `LET`, the module was saved as non-executable. Fix the JCL Binder step to include the missing library:
```jcl
//LKED.SYSLIB DD DSN=CEE.SCEELKED,DISP=SHR
//            DD DSN=PROD.COBOL.LOADLIB,DISP=SHR
//            DD DSN=PROD.SUBROUTINES.LOADLIB,DISP=SHR
```

### 2. Verify Dynamic vs Static CALL Syntax
If the subprogram is meant to be loaded dynamically at runtime, ensure the module name is in a variable or compile with `DYNAM`:
```cobol
      * DYNAMIC CALL - loaded from STEPLIB at runtime
       MOVE 'SUBPGM1' TO WS-SUBPROGRAM-NAME.
       CALL WS-SUBPROGRAM-NAME USING WS-DATA-PAYLOAD.
```
In JCL, verify that `PROD.SUBROUTINES.LOADLIB` is included in the runtime `STEPLIB` or `JOBLIB` concatenation.

### 3. Check CICS Program Definition (CSD / BAS)
In CICS, verify that the program is installed in the CSD:
```text
CEMT INQUIRE PROGRAM(SUBPGM1)
```
Ensure the program status is `ENA` (Enabled) and `PRO` (Program). If `STATUS: DIS` (Disabled), issue `CEMT SET PROGRAM(SUBPGM1) ENA NEWCOPY`.""",
        "prevention": [
            "Set Linkage Editor / Binder return code threshold `MAXRC=0` or `MAXRC=4`. Never deploy a module if Binder issues `RC=08`.",
            "Standardize on Enterprise COBOL 6.x with `AMODE(31),RMODE(ANY)` across all application components.",
            "Use automated Endevor/ChangeMan build processors with strict dependency validation rules.",
            "Test dynamic `CALL` targets using automated CI/CD pipelines before promoting load modules to production."
        ],
        "references": [
            {"title": "IBM z/OS MVS Program Management: User's Guide and Reference", "url": "https://www.ibm.com/docs/en/zos/latest?topic=binder-link-editing-programs"},
            {"title": "IBM z/OS MVS System Codes: Completion Code 0C1", "url": "https://www.ibm.com/docs/en/zos/latest?topic=codes-0c1"},
            {"title": "StackMF Broadcom Endevor Replacement & CI/CD Services", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },

    # -------------------------------------------------------------------------
    # 5. ASRA ABEND IN CICS COMMAND LEVEL & CEDF DEBUGGING
    # -------------------------------------------------------------------------
    {
        "slug": "asra-abend-cics-debugging-cedf",
        "title": "Resolving ASRA ABENDs in IBM CICS TS: Command-Level Debugging & CEDF Analysis",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["CICS", "ASRA", "CEDF", "COBOL", "Dump Analysis", "Storage Violation"],
        "reading_time": "10 min read",
        "tldr": "CICS ASRA is the general transaction abend code indicating a program check (S0C4, S0C7, S0C1, etc.) inside an online transaction. Learn how to locate the execution offset in the CICS Transaction Dump, use CEDF and CEBR to inspect storage, and fix transaction failures.",
        "problem": """A customer service representative enters transaction `TX40` on a 3270 terminal. The screen flashes:
```text
DFHAC2206 14:15:02 CICS01 TRANSACTION TX40 ABENDED ASRA IN PROGRAM CUSTINQ.
          UPDATES TO RECOVERABLE RESOURCES WILL BE BACKED OUT.
```
CICS writes a transaction dump to `DFHDMPA`/`DFHDMPB`. End users report the transaction unavailable, and the CICS region log shows repetitive ASRA occurrences under load.""",
        "root_cause": """CICS intercepts all hardware program checks (operating system interrupts 01 through 15) and classifies them as transaction abend `ASRA`:
- **Interrupt 07 (Data Exception / S0C7)**: 65% of all ASRAs. Caused by non-numeric data in packed fields in `DFHCOMMAREA` or TS queues.
- **Interrupt 04 (Protection Exception / S0C4)**: 30% of ASRAs. Caused by bad pointers, unallocated `CONTAINER` storage, or subscript overruns.
- **Interrupt 01 (Operation Exception / S0C1)**: 5% of ASRAs. Bad module linking or corrupt branch vectors.

Because CICS shields the operating system from crashing, it invokes the CICS Condition Handler, captures diagnostic registers, backs out recoverable database changes via Dynamic Transaction Backout (DTB), and issues message `DFHAC2206`.""",
        "solution": """### 1. Identify the Exact PSW and Program Offset
Open the CICS Transaction Dump in IPCS or your dump viewer (e.g., IBM Fault Analyzer or Sysview):
1. Locate the `PSW AT ENTRY TO ABEND`:
   `PSW: 078D1000 85A21480`
2. Locate the load point of the program `CUSTINQ`:
   `PROGRAM CUSTINQ LOAD POINT: 85A20000`
3. Compute the offset:
   `85A21480 - 85A20000 = +001480`
4. Open the compiler listing for `CUSTINQ` generated with `LIST` or `OFFSET`. Look up offset `+001480` to find the exact source statement (e.g., line 412).

### 2. Interactive Debugging with CEDF
In your CICS test region, activate the Execution Diagnostic Facility:
```text
CEDF
```
Then initiate transaction `TX40`. CEDF intercepts every CICS command:
- Press `PF5` to inspect Working-Storage.
- Check the values of Commarea variables before calling dependent services.
- When the crash occurs, CEDF displays the exact instruction, registers, and memory dump before abending.

### 3. Inspect Temporary Storage with CEBR
If the program reads records from a CICS TS Queue, inspect the queue contents:
```text
CEBR TSQ_CUST_DATA
```
Verify whether any record contains non-printable EBCDIC garbage or un-cleared null bytes.""",
        "prevention": [
            "Implement automated boundary checks on all CICS Channel and Container payloads before parsing.",
            "Enable CICS Storage Protection and Transaction Isolation (`TRANISO=YES`) in the SIT to isolate buggy transactions.",
            "Use IBM Fault Analyzer or modern OpenTelemetry CICS agents to automatically capture source-level stack traces.",
            "Enforce strict Commarea contract validation using OpenAPI schemas when integrating via z/OS Connect."
        ],
        "references": [
            {"title": "IBM CICS Transaction Server for z/OS: ASRA Abend Diagnosis", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=dumps-investigating-asra-abend"},
            {"title": "IBM CICS TS: Using CEDF to Debug Applications", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=cedf-testing-your-application"},
            {"title": "StackMF 24/7 Managed Mainframe Application Support (AMS)", "url": "https://stackmf.com/#maintenance-ams"}
        ]
    },

    # -------------------------------------------------------------------------
    # 6. AEY9 ABEND IN CICS RACF / SECURITY CHECKING
    # -------------------------------------------------------------------------
    {
        "slug": "aey9-abend-cics-security-racf",
        "title": "Fixing CICS AEY9 ABEND: Transaction & Resource Security Key Check Failures",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["CICS", "AEY9", "RACF", "Security", "ACF2", "Top Secret"],
        "reading_time": "7 min read",
        "tldr": "CICS ABEND AEY9 occurs when a user or surrogate identity attempts to execute a transaction or access a protected CICS resource (file, program, TS queue) without required RACF, ACF2, or Top Secret authorization. Understand ESM class definitions and command security.",
        "problem": """Users authenticate to CICS or call a CICS REST API through z/OS Connect and receive:
```text
DFHAC2001 11:30:14 CICS01 TRANSACTION TX99 ABENDED AEY9 IN PROGRAM ORDR01.
          SECURITY CHECK FAILURE FOR USER APPLUSER.
ICH408I USER(APPLUSER) GROUP(FINGRP) NAME(APP INTEGRATION)
  CICS01.PAYROLL.MASTER CL(FCICSFMP)
  INSUFFICIENT ACCESS AUTHORITY
  FROM CICS01.PAYROLL.* (G)
  ACCESS INTENT(UPDATE)  ACCESS ALLOWED(READ)
```
The transaction halts, throwing HTTP 500 to modern web front-ends or kicking terminal operators out of the system.""",
        "root_cause": """When CICS is configured with security enabled (`SEC=YES` in the System Initialization Table - SIT), CICS invokes the external security manager (IBM RACF, Broadcom ACF2, or Broadcom Top Secret) for:
1. **Transaction Attachment Security (TCICSTRN)**: Does `APPLUSER` have `READ` authority to execute transaction `TX99`?
2. **Resource Security Checking (RESSEC / XFCT / XPCT / XJCT)**: Does the transaction have permission to perform `UPDATE` or `READ` against the target VSAM file (`FCICSFMP`), temporary storage queue (`JCICSJCT`), or program (`PCICSPCT`)?
3. **Surrogate Security**: In web service or MQ triggered transactions, is the regional default user authorized to act as surrogate for the incoming authenticated user identity?

If the external security manager returns RC=08 (Not Authorized), CICS immediately terminates the task with ABEND AEY9.""",
        "solution": """### 1. Identify the Exact RACF Class and Profile
Inspect the `ICH408I` console syslog message:
- User ID: `APPLUSER`
- Class: `FCICSFMP` (CICS File Control)
- Resource: `CICS01.PAYROLL.MASTER`
- Required Access: `UPDATE`

### 2. Grant the Missing RACF Permissions
Have the security administrator issue RACF commands:
```text
PERMIT CICS01.PAYROLL.MASTER CLASS(FCICSFMP) ID(FINGRP) ACCESS(UPDATE)
SETROPTS RACLIST(FCICSFMP) REFRESH
```
If using general grouping profiles, refresh the group class:
```text
SETROPTS RACLIST(GCICSTRN) REFRESH
```

### 3. Handle Command Security in Application Code
If the application needs to gracefully handle permission denials without crashing with AEY9, use the `NOHANDLE` or `RESP` option in the CICS command:
```cobol
       EXEC CICS READ
                 FILE('PAYROLL-MASTER')
                 INTO(WS-PAYROLL-RECORD)
                 RIDFLD(WS-EMP-ID)
                 RESP(WS-RESP-CODE)
                 RESP2(WS-RESP2-CODE)
       END-EXEC.

       IF WS-RESP-CODE = DFHRESP(NOTAUTH)
           MOVE 'Security Error: Unauthorized File Access'
             TO WS-ERROR-MSG
           PERFORM 9900-DISPLAY-AUTH-ERROR
       END-IF.
```""",
        "prevention": [
            "Always include `RESP(WS-RESP-CODE)` on all CICS file, queue, and link statements to intercept `NOTAUTH` gracefully.",
            "Maintain automated RACF profile auditing during Endevor/Git promotion pipelines to prevent untested security configurations from entering production.",
            "Verify surrogate user authorizations (`SURROGAT` class) when standing up z/OS Connect API providers.",
            "Periodically review CICS SIT parameters `CMDSEC=ALWAYS` and `RESSEC=ALWAYS` across regions."
        ],
        "references": [
            {"title": "IBM CICS TS: Security checking and AEY9 abend handling", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=security-troubleshooting-cics-security"},
            {"title": "IBM z/OS Security Server RACF Command Language Reference", "url": "https://www.ibm.com/docs/en/zos/latest?topic=commands-permit"},
            {"title": "StackMF Modernization Bridge: Secure z/OS Connect Integration", "url": "https://stackmf.com/#fullstack-bridge"}
        ]
    },

    # -------------------------------------------------------------------------
    # 7. U4038 LE RUNTIME ABEND IN BATCH & CEEDUMP
    # -------------------------------------------------------------------------
    {
        "slug": "u4038-le-runtime-abend-troubleshooting",
        "title": "Taming Language Environment (LE) User ABEND U4038: CEEDUMP Analysis & TRAP Tuning",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["LE", "U4038", "CEEDUMP", "COBOL", "z/OS", "Diagnostics"],
        "reading_time": "9 min read",
        "tldr": "User ABEND U4038 occurs when an unhandled condition of severity 2 or greater terminates a Language Environment (LE) enclave. Learn how to decipher the CEEDUMP traceback, inspect condition tokens, and configure runtime options like TERMTHDACT and TRAP.",
        "problem": """A core batch processing step terminates with:
```text
CEE0374C CONDITION=CEE3207S TOKEN=00030C87 59C3C5C5 00000000 
         ORIGIN=IGZINSH4 CALLED BY=MODPAY01 OFFSET=+00001B42
CEE3DMP V2 R4 M00: ALL CONDITIONS UNHANDLED - ENCLAVE TERMINATED
IEF450I JOBPAY01 STEP020 - ABEND=U4038 U0000 REASON=00000001
```
The developer sees only `ABEND=U4038`, which is a generic wrapper code, leaving them puzzled about what actually failed inside the COBOL program.""",
        "root_cause": """IBM Language Environment (LE) provides a unified runtime environment for COBOL, PL/I, C/C++, and Fortran on z/OS. When an internal failure occurs (such as an unhandled divide-by-zero, file status mismatch, or system abend S0C7/S0C4):
1. The LE Condition Manager intercepts the hardware interrupt or software error.
2. It attempts to locate a user condition handler registered via `CEEHDLR`.
3. If no handler exists or the handler percolates the condition, and its severity is 2 (Error), 3 (Severe Error), or 4 (Critical Error), LE terminates the enclave.
4. LE forces an operating system ABEND U4038 (Reason Code 01) to ensure the job step fails and transactional changes are rolled back.""",
        "solution": """### 1. Configure TERMTHDACT to Generate a Full CEEDUMP
By default, some environments suppress the full diagnostic dump. In your JCL, pass LE runtime options via the `PARM` parameter or `//CEEOPTS` DD:
```jcl
//STEP020  EXEC PGM=MODPAY01
//CEEOPTS  DD *
  TERMTHDACT(UADUMP),
  TRAP(ON,SPIE),
  STORAGE(00,00,00,0K)
/*
//CEEDUMP  DD SYSOUT=*
```
`TERMTHDACT(UADUMP)` instructs LE to generate both a formatted CEEDUMP and an MVS system dump (SYSMDUMP) with complete call stack traceback.

### 2. Read the CEEDUMP Traceback Section
Open the `CEEDUMP` spool file. Search for `Traceback:`:
```text
Traceback:
  DSA   Entry       E  Offset  Statement   Load Mod    Program Unit
  1     CEEHDSP     +000041B4              CEEPLPKA    CEEHDSP
  2     IGZINSH4    +0000021A              IGZCPCO     IGZINSH4
  3     PROCESS-TAX +000005C2  482         PAYMOD01    PAYMOD01
  4     MAIN-LOGIC  +000001F0  120         PAYMOD01    PAYMOD01
```
This pinpointed the failure to statement 482 inside paragraph `PROCESS-TAX` of program `PAYMOD01`.

### 3. Handle Conditions Gracefully in Source Code
Use COBOL condition handling or defensive status inspection to avoid unhandled enclave termination:
```cobol
       CALL 'CEEHDLR' USING BY REFERENCE WS-HANDLER-ROUTINE
                            WS-TOKEN
                            WS-FBCODE.
```""",
        "prevention": [
            "Always include `//CEEDUMP DD SYSOUT=*` in all batch JCL job streams.",
            "Use `TERMTHDACT(TRACE)` in production and `TERMTHDACT(UADUMP)` in testing environments.",
            "Do not set `TRAP(OFF)` unless running vendor diagnostic tools; `TRAP(ON)` is mandatory for LE cleanup.",
            "Examine the root condition token in the traceback rather than stopping at the generic U4038 code."
        ],
        "references": [
            {"title": "IBM Language Environment Debugging Guide: Understanding U4038", "url": "https://www.ibm.com/docs/en/zos/latest?topic=troubleshooting-abend-u4038"},
            {"title": "IBM Language Environment Customization: TERMTHDACT Options", "url": "https://www.ibm.com/docs/en/zos/latest?topic=descriptions-termthdact"},
            {"title": "StackMF Mainframe Application Development & AMS", "url": "https://stackmf.com/#maintenance-ams"}
        ]
    },

    # -------------------------------------------------------------------------
    # 8. U0778 & U0777 IMS DB/DC DEADLOCK RESOLUTION
    # -------------------------------------------------------------------------
    {
        "slug": "u0778-u0777-ims-dc-deadlock-resolution",
        "title": "Resolving IMS DB/DC U0777 and U0778 Deadlocks in Fast Path & Full-Function Databases",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["IMS DB", "IMS DC", "U0777", "U0778", "DL/I", "Fast Path", "Deadlocks"],
        "reading_time": "9 min read",
        "tldr": "IMS U0777 and U0778 pseudo-abends occur when two concurrent Message Processing Programs (MPP) or BMP batch jobs deadlock while competing for database segments or Fast Path DEDB control intervals. Learn lock sequence structuring, commit strategies, and lock timeout tuning.",
        "problem": """High-concurrency IMS online message processing programs (MPP) terminate with:
```text
DFS554A JOBMPP01 STEP010 TRANS TXINV1 ABEND U0778
DFS555I TRANSACTION TXINV1 TERMINATED WITH REASON CODE 00000000
```
In batch message processing (BMP) jobs, steps fail with `ABEND=U0777`, requiring operator intervention to requeue input messages or restart the database block.""",
        "root_cause": """In IBM IMS Database Manager:
- **U0777 (Pseudo-Abend)**: Indicates a database deadlock between two or more application programs contending for the same DL/I database segment, buffer, or Fast Path DEDB Control Interval. IMS dynamically terminates one of the tasks (the 'victim'), rolls back uncommitted changes to the last syncpoint, and automatically requeues the input transaction message for retry up to the system limit.
- **U0778 (Unsuccessful Retry / Deadlock Exceeded)**: Occurs when an MPP transaction repeatedly hits a deadlock condition during automatic retry attempts or when a BMP program deadlocks without commit syncpoint restart capability.

Deadlocks occur when Program A locks Segment 1 and requests Segment 2, while Program B locks Segment 2 and requests Segment 1.""",
        "solution": """### 1. Enforce Consistent Root-Key Access Order
All programs accessing multiple database records or segments must access keys in strictly ascending alphanumeric sequence:
```cobol
      * BAD: Updating accounts in random order received from web payload
      * GOOD: Sort input keys before issuing DL/I calls
       PERFORM VARYING WS-IDX FROM 1 BY 1 UNTIL WS-IDX > WS-COUNT
           MOVE WS-SORTED-ACCT(WS-IDX) TO DB-ACCT-KEY
           CALL 'CBLTDLI' USING GHU
                                ACCOUNT-PCB
                                ACCOUNT-SEGMENT
                                ACCOUNT-SSA
           PERFORM 2000-PROCESS-UPDATE
           CALL 'CBLTDLI' USING REPL
                                ACCOUNT-PCB
                                ACCOUNT-SEGMENT
       END-PERFORM.
```

### 2. Implement Frequent CHKP (Checkpoints) in BMPs
Batch BMP jobs holding locks for thousands of records starve MPPs. Insert periodic checkpoint calls:
```cobol
       ADD 1 TO WS-TX-COUNT
       IF WS-TX-COUNT > 500
           CALL 'CBLTDLI' USING CHKP
                                CHKP-PCB
                                CHKP-LEN
                                CHKP-ID
           MOVE 0 TO WS-TX-COUNT
       END-IF.
```

### 3. Tune IRLM Lock Timeouts
For Full-Function databases utilizing IRLM (Internal Resource Lock Manager), adjust the lock timeout parameter in `BPECFG` / `IRLMPROC`:
```text
DEADLOK=(1,5)
```
- First parameter (`1` sec): Frequency of local deadlock cycle detection.
- Second parameter (`5` cycles): Global sysplex deadlock sweep interval.""",
        "prevention": [
            "Access database segments in uniform hierarchical order (Root -> Child -> Dependent).",
            "Keep online MPP execution times under 100 milliseconds; offload heavy batch processing to BMPs.",
            "Use Fast Path DEDB with subset pointers and segment partitioning for hyper-concurrent financial ledgers.",
            "Analyze IMS Monitor reports (`DFSSTAT`) to track lock wait queues and contention rates."
        ],
        "references": [
            {"title": "IBM IMS Messages and Codes: Volume 3 (U0777 and U0778)", "url": "https://www.ibm.com/docs/en/ims/latest?topic=codes-u0777"},
            {"title": "IBM IMS Database Administration: Concurrency and Locking", "url": "https://www.ibm.com/docs/en/ims/latest?topic=admin-locking-database-concurrency"},
            {"title": "StackMF Mainframe Core Engineering Services", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },

    # -------------------------------------------------------------------------
    # 9. DB2 SQLCODE -911 & -904 RESOURCE UNAVAILABLE & DEADLOCKS
    # -------------------------------------------------------------------------
    {
        "slug": "db2-sqlcode-911-904-resource-unavailable-deadlocks",
        "title": "Resolving DB2 SQLCODE -911 (Reason 00C90088 / Deadlock) and -904 Resource Unavailable",
        "date": "2026-09-27",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "SQLCODE -911", "SQLCODE -904", "Deadlocks", "IRLM", "COBOL DB2"],
        "reading_time": "11 min read",
        "tldr": "DB2 SQLCODE -911 indicates your unit of work was rolled back due to a deadlock (Reason 00C90088) or lock timeout (Reason 00C9008E). SQLCODE -904 indicates an unavailable resource (tablespace locked, thread limit exceeded). Discover root causes and concurrency tuning.",
        "problem": """Production transactions and overnight batch update suites crash with:
```text
DSNT408I SQLCODE = -911, ERROR:  THE CURRENT UNIT OF WORK HAS BEEN ROLLED BACK DUE
         TO DEADLOCK OR TIMEOUT. REASON 00C90088, TYPE OF RESOURCE 00000302,
         RESOURCE NAME DSN8D13A.DSN8S13E
DSNT418I SQLSTATE   = 40001 SQLSTATE RETURN CODE
```
Or in peak periods:
```text
DSNT408I SQLCODE = -904, ERROR:  UNSUCCESSFUL EXECUTION CAUSED BY AN UNAVAILABLE
         RESOURCE. REASON 00C90084, TYPE 00000200, NAME DSN8D13A
```
Application threads are terminated, requiring manual transaction re-submits and delaying financial closing windows.""",
        "root_cause": """DB2 for z/OS concurrency is orchestrated by the Internal Resource Lock Manager (IRLM):
1. **SQLCODE -911 / Reason 00C90088 (Deadlock)**: Two threads requested exclusive (`X`) or update (`U`) locks on database pages or rows held by each other in cyclical dependency. IRLM selects one as the 'victim' and rolls back its uncommitted SQL statements.
2. **SQLCODE -911 / Reason 00C9008E (Timeout)**: A thread waited longer than the IRLM timeout value (defined in DSNZPARM `IRLMRWT`, typically 30 or 60 seconds) for a lock to be released.
3. **SQLCODE -904 / Reason 00C90084 (Max Lock Escaped / Space Limit)**: A utility (e.g., REORG, LOAD) has exclusive access to the tablespace, or maximum active threads (`CTHREAD` / `MAXDBAT`) were exhausted.""",
        "solution": """### 1. Identify the Competitor Threads via DB2 Diagnostic Logs
Query the MVS Syslog or DB2 MSTR/DIST address space logs for message `DSNT375I` / `DSNT376I`:
```text
DSNT375I  PLAN=PLNPAY01 WITH CORRELATION ID=PAYJOB1 IS HOLDING A LOCK
DSNT376I  PLAN=PLNWEB01 WITH CORRELATION ID=ODBC_SRV WAS WAITING
```
This isolates the exact two programs colliding on resource `DSN8S13E`.

### 2. Implement Retry Logic in Application Code
For online transactions and MQ/Kafka listeners, catch `-911` and retry before failing:
```cobol
       EXEC SQL
           UPDATE ACCOUNT_BALANCE
           SET BALANCE = BALANCE - :WS-TX-AMOUNT
           WHERE ACCOUNT_ID = :WS-ACCT-ID
       END-EXEC.

       IF SQLCODE = -911
           ADD 1 TO WS-RETRY-COUNT
           IF WS-RETRY-COUNT <= 3
      * Small exponential backoff
               CALL 'CEESGL' ...
               PERFORM 1000-REEXECUTE-TX
           ELSE
               PERFORM 9900-LOG-DEADLOCK-ABEND
           END-IF
       END-IF.
```

### 3. Enforce Frequent Commits in Batch Jobs
Never run long-running batch updates without periodic `COMMIT`:
```cobol
       ADD 1 TO WS-RECS-SINCE-COMMIT
       IF WS-RECS-SINCE-COMMIT > 1000
           EXEC SQL COMMIT END-EXEC
           MOVE 0 TO WS-RECS-SINCE-COMMIT
       END-IF.
```

### 4. Optimize Concurrency Bind Options
Bind packages with:
- `ISOLATION(CS)` (Cursor Stability)
- `CURRENTDATA(NO)`
- `CONCURRENTACCESSRESOLUTION(USECURRENTLYCOMMITTED)`: Allows queries to read the previous committed version of a row rather than waiting for an in-flight update lock to release!""",
        "prevention": [
            "Bind all read-heavy queries with `CONCURRENTACCESSRESOLUTION(USECURRENTLYCOMMITTED)` to eliminate reader-writer contention.",
            "Always update tables in a uniform alphabetical and key order across all application components.",
            "Tune DSNZPARM `IRLMRWT` (Resource Wait Time) and `DEADLOK` sweep frequencies appropriately.",
            "Ensure batch programs commit every 500 to 2,000 updates to release row/page locks."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS Codes: SQLCODE -911 Details", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=codes-911"},
            {"title": "IBM Db2 13 for z/OS Managing Concurrency and Locking", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=performance-concurrency-locking"},
            {"title": "StackMF DB2 Performance Tuning & Modernization", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },

    # -------------------------------------------------------------------------
    # 10. DB2 STAGE 1 VS STAGE 2 PREDICATES TUNING
    # -------------------------------------------------------------------------
    {
        "slug": "db2-stage-1-vs-stage-2-predicates-tuning",
        "title": "DB2 z/OS Query Optimization: Converting Stage 2 (Residual) into Stage 1 (Indexable) Predicates",
        "date": "2026-09-27",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "SQL Tuning", "EXPLAIN", "Stage 1", "Stage 2", "PLAN_TABLE"],
        "reading_time": "10 min read",
        "tldr": "In DB2 for z/OS, Stage 1 (sargable) predicates are evaluated inside the Data Manager (DM) at near-hardware speeds, while Stage 2 (residual) predicates require transferring rows to the Relational Data System (RDS), burning massive CPU. Learn how to refactor SQL for Stage 1 execution.",
        "problem": """A core query scanning a 50-million-row customer table consumes 45 CPU seconds per execution:
```sql
SELECT CUST_ID, CUST_NAME, CURRENT_BALANCE
FROM CUSTOMER_TABLE
WHERE CUST_STATUS || CUST_REGION = 'A' || 'EAST'
  AND YEAR(LAST_LOGIN_DATE) = 2026;
```
When running DB2 EXPLAIN, the developer sees `STAGE='2'` in `DSN_PREDICAT_TABLE`. The query causes massive I/O buffer pool churn and inflates the enterprise 4HRA MIPS billing peak.""",
        "root_cause": """DB2 executes SQL through a two-tiered processing pipeline:
1. **Stage 1 (Data Manager / DM / Sargable)**: Evaluated directly as rows are read from disk or buffer pools. Non-qualifying rows are discarded immediately without CPU-intensive context switching.
2. **Stage 2 (Relational Data System / RDS / Residual)**: Rows passing Stage 1 must be packaged into internal structures and passed across internal component boundaries to RDS for evaluation.

When developers wrap columns in scalar functions (`YEAR(COL)`, `SUBSTR(COL)`, `COL1 || COL2`), use mismatched datatypes (e.g., comparing `VARCHAR` to `INTEGER`), or use expressions on indexable columns, the DB2 query optimizer cannot use an index and is forced to push evaluation into Stage 2.""",
        "solution": """### 1. Inspect DSN_PREDICAT_TABLE via EXPLAIN
Run `EXPLAIN ALL SET QUERYNO = 101 FOR ...` and check predicate stages:
```sql
SELECT PREDNO, STAGE, TYPE, PREDICATE_TEXT
FROM DSN_PREDICAT_TABLE
WHERE QUERYNO = 101;
```
Look for any predicate where `STAGE = '2'`.

### 2. Refactor Scalar Functions into Range Predicates
Avoid function wrappers on columns in the `WHERE` clause:
```sql
-- SLOW (Stage 2 - Full scan of all rows):
WHERE YEAR(LAST_LOGIN_DATE) = 2026

-- FAST (Stage 1 / Indexable Range Search):
WHERE LAST_LOGIN_DATE >= '2026-01-01-00.00.00.000000'
  AND LAST_LOGIN_DATE <= '2026-12-31-23.59.59.999999'
```

### 3. Separate Concatenated Columns
Never concatenate columns on the left-hand side of a comparison:
```sql
-- SLOW (Stage 2):
WHERE CUST_STATUS || CUST_REGION = 'AEAST'

-- FAST (Stage 1 - Indexable composite match):
WHERE CUST_STATUS = 'A'
  AND CUST_REGION = 'EAST'
```

### 4. Match Host Variable Datatypes Exactly
In COBOL programs, ensure host variables match the DB2 catalog column definition:
- If column is `DECIMAL(9,2)`, host variable must be `PIC S9(7)V99 COMP-3`.
- If host variable is defined as `PIC X(10)` or integer, DB2 must perform type conversion at runtime, degrading the predicate to Stage 2.""",
        "prevention": [
            "Integrate DB2 EXPLAIN checks into automated Endevor/Git pull request pipelines.",
            "Never apply scalar functions to indexed columns; rewrite as explicit range boundaries.",
            "Ensure COBOL host variable datatypes exactly replicate DB2 DCLGEN definitions.",
            "Create generated columns or expression-based indexes (`CREATE INDEX ... ON TABLE (YEAR(DATE_COL))`) if SQL cannot be refactored."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS Managing Performance: Predicate Processing", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=queries-predicate-processing"},
            {"title": "IBM Redbooks: Subsystem and Transaction Monitoring with Db2 for z/OS", "url": "https://www.redbooks.ibm.com/abstracts/sg248182.html"},
            {"title": "StackMF Enterprise Mainframe Modernization & DB2 Tuning", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },

    # -------------------------------------------------------------------------
    # 11. DB2 RUNSTATS & INDEX CLUSTERING FOR OPTIMIZER
    # -------------------------------------------------------------------------
    {
        "slug": "db2-runstats-index-clustering-optimizer",
        "title": "How Outdated RUNSTATS Cause Catastrophic Tablespace Scans in DB2 for z/OS",
        "date": "2026-09-27",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "RUNSTATS", "Optimizer", "Catalog", "Index Clustering", "PLAN_TABLE"],
        "reading_time": "9 min read",
        "tldr": "When RUNSTATS statistics are stale or missing, the DB2 Cost-Based Optimizer makes catastrophic access path choices, selecting full tablespace scans over clustered indexes. Master RUNSTATS parameters, real-time statistics (RTS), and access path stability.",
        "problem": """A daily report query that normally finishes in 2 minutes suddenly runs for 90 minutes after an end-of-quarter data load:
```text
DSNA672I QUERY RUNTIME EXCEEDED THRESHOLD: 5400 SECONDS
ACCESSTYPE IN PLAN_TABLE: 'R' (TABLESPACE SCAN) INSTEAD OF 'I' (INDEX SCAN)
```
System programmers observe 100% DASD channel utilization on the volume holding the tablespace, while CPU consumption spikes drastically.""",
        "root_cause": """The DB2 Cost-Based Optimizer determines the access path during `BIND` or dynamic SQL preparation based on statistics stored in the DB2 Catalog tables (`SYSIBM.SYSTABLES`, `SYSIBM.SYSINDEXES`, `SYSIBM.SYSCOLDIST`):
1. **Stale Statistics**: If a table grew from 10,000 rows to 10,000,000 rows without running `RUNSTATS`, the optimizer believes the table is tiny and assumes a tablespace scan (`ACCESSTYPE='R'`) is cheaper than traversing index tree levels.
2. **Degraded Cluster Ratio**: If `CLUSTERATIO` in `SYSIBM.SYSINDEXES` drops below 80% due to frequent unclustered inserts/updates, the optimizer penalizes the index because fetching data pages requires random rather than sequential I/O.
3. **Data Skew**: When 90% of rows have `STATUS = 'C'` and 10% have `STATUS = 'P'`, standard cardinality without column distribution statistics causes the optimizer to assume uniform distribution.""",
        "solution": """### 1. Execute Production-Grade RUNSTATS Utility
Run `RUNSTATS` with column distribution statistics and sampling:
```jcl
//RUNSTAT1 EXEC DSNUPROC,PARM='DB2P,RUNSTATS'
//SYSIN    DD *
  RUNSTATS TABLESPACE DSN8D13A.DSN8S13D
    TABLE(ALL)
    INDEX(ALL)
    KEYCARD
    FREQVAL NUMCOLS 1 COUNT 25
    HISTOGRAM NUMCOLS 1 NUMQUANTILES 20
    SHRLEVEL CHANGE
/*
```
- `KEYCARD`: Collects distinct key cardinalities for composite index prefixes.
- `FREQVAL`: Collects the 25 most frequent values to handle data skew.
- `HISTOGRAM`: Creates distribution quantiles for range predicates (`BETWEEN`, `>`, `<`).

### 2. Check Catalog Statistics
Verify updated statistics in the DB2 catalog:
```sql
SELECT CARDF, NPAGES, PCTPAGES
FROM SYSIBM.SYSTABLES
WHERE NAME = 'CUSTOMER_TABLE';

SELECT NAME, CLUSTERING, CLUSTERATIO, NLEAF, NLEVELS
FROM SYSIBM.SYSINDEXES
WHERE TBNAME = 'CUSTOMER_TABLE';
```

### 3. Rebind the Package to Pick Up New Access Paths
Once statistics are refreshed, rebind the affected package:
```text
REBIND PACKAGE(PAYCOLL.APPLMOD1) -
       PLANMGMT(EXTENDED) -
       APREUSE(NO)
```
Using `PLANMGMT(EXTENDED)` ensures the previous access path is preserved in the catalog, allowing immediate fallback via `SWITCH` if performance degrades.""",
        "prevention": [
            "Schedule automated `RUNSTATS` jobs triggered by Real-Time Statistics (RTS) thresholds (e.g., when `TOTALINSERTS + TOTALDELETES > 20%`).",
            "Always specify `KEYCARD` and `FREQVAL` when collecting statistics on indexed columns.",
            "Run `REORG TABLESPACE` before `RUNSTATS` when `CLUSTERATIO` drops below 80% to restore sequential page ordering.",
            "Enable DB2 Access Path Stability (`PLANMGMT=EXTENDED`) for critical packages before executing production rebinds."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS Managing Performance: RUNSTATS Utility", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=utilities-runstats"},
            {"title": "IBM Db2 13 for z/OS Access Path Selection", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=performance-access-paths"},
            {"title": "StackMF Enterprise Broadcom Replacement & Cost Reduction", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },

    # -------------------------------------------------------------------------
    # 12. DB2 LOCK ESCALATION & ISOLATION LEVELS
    # -------------------------------------------------------------------------
    {
        "slug": "db2-lock-escalation-isolation-levels",
        "title": "Preventing DB2 Lock Escalation: Tuning LOCKSIZE, Isolation Levels, and SKIP LOCKED DATA",
        "date": "2026-09-27",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "Lock Escalation", "Concurrency", "Isolation CS", "SKIP LOCKED DATA", "DSNZPARM"],
        "reading_time": "10 min read",
        "tldr": "When a transaction acquires more locks than DSNZPARM NUMLKTS, DB2 automatically escalates page/row locks to an exclusive tablespace lock, freezing out all concurrent users. Learn how to tune LOCKSIZE, use Isolation CS, and implement SKIP LOCKED DATA for high-throughput queues.",
        "problem": """During daytime hours, online CICS and REST API transactions freeze across the enterprise. The console issues alert:
```text
DSNI031I -DB2P DSNITNBD LOCK ESCALATION HAS OCCURRED
          FOR OBJECT TYPE 00000200, NAME DSN8D13A.DSN8S13E
          OCCURRED FOR CORRELATION-ID = BATCHJOB04
          IDENTIFYING BATCH UPDATE IN PROGRESS
```
All online transactions attempting to read or update `DSN8S13E` stall, eventually timing out with SQLCODE -911 Reason 00C9008E.""",
        "root_cause": """Tablespaces defined with `LOCKSIZE ANY` allow DB2 to dynamically choose the lock granularity (page or row). However:
1. When a single thread acquires more individual page/row locks than the subsystem threshold `NUMLKTS` (typically 1,000 to 5,000 locks), DB2 triggers **Lock Escalation**.
2. DB2 promotes the lock on the entire tablespace or partition to an Exclusive (`X`) or Share (`S`) lock and releases all the granular child locks to conserve EDM pool memory.
3. Any other application thread needing access to any row in that tablespace is locked out until the batch transaction issues `COMMIT` or terminates.""",
        "solution": """### 1. Alter Tablespace to Explicit LOCKSIZE
To prevent escalation on high-concurrency tables, define explicit lock sizing:
```sql
ALTER TABLESPACE DSN8D13A.DSN8S13E
      LOCKSIZE ROW
      LOCKMAX 0;
```
`LOCKMAX 0` explicitly disables lock escalation for that specific tablespace, ensuring fine-grained concurrency regardless of `NUMLKTS`.

### 2. Bind with Cursor Stability (CS) and CURRENTDATA(NO)
Review your package BIND parameters:
- Avoid `ISOLATION(RR)` (Repeatable Read) and `ISOLATION(RS)` (Read Stability) unless mathematically required, as they hold share locks on all scanned rows until commit.
- Use `ISOLATION(CS)` with `CURRENTDATA(NO)`: Locks are released immediately as the cursor moves to the next row.

### 3. Implement SKIP LOCKED DATA for Multi-Worker Queue Tables
When multiple worker tasks pick up unprocessed orders or events, use `SKIP LOCKED DATA`:
```sql
SELECT ORDER_ID, PAYLOAD
FROM ORDER_QUEUE
WHERE STATUS = 'READY'
FETCH FIRST 1 ROW ONLY
FOR UPDATE OF STATUS
SKIP LOCKED DATA;
```
Instead of waiting on locks held by competing workers or causing timeouts, DB2 transparently skips locked rows and immediately grabs the next available item, enabling massive linear horizontal scaling!""",
        "prevention": [
            "Set `LOCKMAX 0` on critical tablespaces to prevent unannounced lock escalation.",
            "Use `SKIP LOCKED DATA` on message queue and task dispatcher tables.",
            "Ensure batch programs commit every 500-1000 row modifications.",
            "Audit SQL packages using IBM OMEGAMON or Sysview for long-running uncommitted cursors."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS Concurrency: Lock Escalation", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=locking-lock-escalation"},
            {"title": "IBM Db2 13 for z/OS SKIP LOCKED DATA Clause", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=queries-skip-locked-data"},
            {"title": "StackMF Mainframe Application Maintenance & AMS", "url": "https://stackmf.com/#maintenance-ams"}
        ]
    },

    # -------------------------------------------------------------------------
    # 13. DB2 COBOL STORED PROCEDURES & WLM TUNING
    # -------------------------------------------------------------------------
    {
        "slug": "db2-stored-procedure-cobol-wlm-tuning",
        "title": "Performance Tuning COBOL DB2 Stored Procedures: WLM Environments & APPLCOMPAT",
        "date": "2026-09-27",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "Stored Procedures", "WLM", "COBOL", "APPLCOMPAT", "SQLCODE -471"],
        "reading_time": "9 min read",
        "tldr": "DB2 Stored Procedures running in WLM-managed address spaces can suffer from thread starvation, initialization latency, and SQLCODE -471 timeouts. Discover how to configure WLM NUMTCB parameters, reuse threads with STAYRESIDENT, and manage APPLCOMPAT.",
        "problem": """Modern microservices calling DB2 Stored Procedures via JDBC or z/OS Connect experience sporadic timeouts and failures:
```text
DSNT408I SQLCODE = -471, ERROR:  INVOCATION OF FUNCTION OR PROCEDURE CUSTSP01
         FAILED DUE TO REASON 00E7900C
DSNT418I SQLSTATE = 57030 SQLSTATE RETURN CODE
```
WLM address spaces max out their CPU limits, and thread queues back up into the distributed data facility (DDF).""",
        "root_cause": """DB2 Stored Procedures execute inside Workload Manager (WLM) managed address spaces (`WLM_ENV`):
1. **Thread Starvation (`NUMTCB` Exhaustion)**: Each WLM address space is defined with `NUMTCB` (number of Task Control Blocks, e.g., 8 or 16). If all TCBs are occupied executing long-running procedures and new requests arrive, requests queue up. When the queue timeout is exceeded, DB2 aborts with SQLCODE -471 Reason `00E7900C`.
2. **Reload Overhead (`STAYRESIDENT NO`)**: If the procedure is defined with `STAYRESIDENT NO`, z/OS unloads the COBOL load module after every single call, incurring constant disk I/O and Language Environment enclave initialization penalties.
3. **APPLCOMPAT Mismatches**: Upgrading DB2 function levels (e.g., from V12R1M500 to V13R1M502) while packages are bound with older `APPLCOMPAT` values causes incompatibilities with modern SQL features.""",
        "solution": """### 1. Optimize Stored Procedure DDL Definition
Update the procedure definition in the DB2 catalog:
```sql
ALTER PROCEDURE CUSTSP01
      WLM ENVIRONMENT WLM_DB2_BATCH
      STAY RESIDENT YES
      RUN OPTIONS 'TRAP(ON),STORAGE(00,00,00,0K)'
      COMMIT ON RETURN NO;
```
- `STAY RESIDENT YES`: Keeps the COBOL load module cached in storage across invocations, eliminating reload overhead.
- `RUN OPTIONS`: Pre-configures Language Environment runtime settings to avoid repeated LE enclave recreation.

### 2. Configure WLM Application Environment NUMTCB
In the z/OS WLM ISPF policy editor:
1. Navigate to `Application Environments`.
2. Select the target WLM environment (e.g., `WLM_DB2_BATCH`).
3. Set `NUMTCB` based on CPU capacity (typically between `10` and `25` for COBOL programs).
4. Set `DYNAMIC SYSTEMS` to `YES` to allow WLM to spin up additional server address spaces automatically during traffic spikes.

### 3. Manage APPLCOMPAT During Migration
When binding the COBOL Stored Procedure package, align `APPLCOMPAT`:
```text
BIND PACKAGE(DB2PROD.CUSTSP01) -
     MEMBER(CUSTSP01) -
     APPLCOMPAT(V13R1M500) -
     ISOLATION(CS) -
     RELEASE(COMMIT)
```""",
        "prevention": [
            "Always define high-volume OLTP stored procedures with `STAY RESIDENT YES`.",
            "Separate CPU-intensive batch stored procedures from lightweight OLTP stored procedures into distinct WLM Application Environments.",
            "Monitor WLM delay states using RMF / SMF Type 72 records to verify server address space responsiveness.",
            "Enforce standardized `APPLCOMPAT` levels across all enterprise DevOps build scripts."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS Application Programming and SQL Guide: Stored Procedures", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=procedures-stored"},
            {"title": "IBM z/OS MVS Planning: Workload Management (WLM)", "url": "https://www.ibm.com/docs/en/zos/latest?topic=wlm-planning-workload-management"},
            {"title": "StackMF Full-Stack Mainframe Bridge Architecture", "url": "https://stackmf.com/#fullstack-bridge"}
        ]
    },

    # -------------------------------------------------------------------------
    # 14. VSAM FILE STATUS 92 & 93 IN BATCH & CICS
    # -------------------------------------------------------------------------
    {
        "slug": "vsam-file-status-92-93-dynamic-allocation",
        "title": "Diagnosing VSAM File Status 92 and 93: Enqueue Locks & Dynamic Allocation Contention",
        "date": "2026-09-27",
        "category": "CICS & VSAM Architecture",
        "tags": ["VSAM", "File Status 92", "File Status 93", "CICS", "COBOL", "IDCAMS", "DISP=SHR"],
        "reading_time": "8 min read",
        "tldr": "VSAM File Status 92 indicates a logic error (e.g. attempting to OPEN an already opened file), while File Status 93 signals resource contention (dataset locked by CICS or another batch job). Learn how to diagnose exclusive enqueue locks and configure non-disruptive access.",
        "problem": """A batch job updating a critical VSAM Key Sequenced Data Set (KSDS) fails with:
```text
PROG010: ERROR OPENING VSAM FILE 'PROD.KSDS.CUSTOMER'
FILE STATUS = 93
CEE3250C The system or user abend U4038 was issued.
```
Or in an online CICS transaction:
```text
FILE STATUS = 92 ON OPEN
CICS RESP=NOTOPEN (RESP2=12)
```
Production schedules back up while operators scramble to determine which job or CICS region holds the dataset lock.""",
        "root_cause": """In COBOL execution against VSAM clusters:
1. **File Status 92 (Logic Error)**: Occurs when a program attempts an operation that violates VSAM state logic:
   - Issuing `OPEN` on a file that is already open.
   - Issuing `READ NEXT` without a successful prior `START` or `READ`.
   - Issuing `REWRITE` without a prior successful `READ` with lock.
2. **File Status 93 (Resource Unavailable / Exclusive Enqueue)**: Occurs when:
   - The dataset is allocated with `DISP=OLD` or `DISP=SHR` without `SHAREOPTIONS(2,3)` or `(3,3)` in the IDCAMS cluster definition.
   - A CICS region holds an exclusive open lock (`FCT` status `OPEN, ENABLED`) for updates, and a batch job attempts to open the dataset for output (`OPEN I-O` or `OPEN EXTEND`).
   - MVS GRS (Global Resource Serialization) holds major name `SPFDSN` or `SYSDSN` on the cluster.""",
        "solution": """### 1. Identify Who Holds the Dataset Lock via TSO / SDSF
From the MVS master console or SDSF, issue:
```text
/D GRS,RES=(*,PROD.KSDS.CUSTOMER)
```
Output reveals the job or CICS region holding the exclusive enqueue:
```text
ISV001I GRS STATUS:
  JOBNAME: CICSPROD  STATUS: EXCLUSIVE  MAJOR: SYSDSN
  JOBNAME: BATCHJOB  STATUS: WAITING
```

### 2. Configure CICS CEMT to Close the File for Batch
Before running the batch update, close and disable the file in CICS:
```text
CEMT SET FILE(CUSTFILE) CLOSED DISABLED
```
Once batch finishes, reopen:
```text
CEMT SET FILE(CUSTFILE) OPEN ENABLED
```

### 3. Review IDCAMS SHAREOPTIONS
Inspect the cluster definition:
```jcl
//STEP1    EXEC PGM=IDCAMS
//SYSPRINT DD SYSOUT=*
//SYSIN    DD *
  LISTCAT ENT('PROD.KSDS.CUSTOMER') ALL
/*
```
Check `SHAREOPTIONS`:
- `SHAREOPTIONS(1 3)`: Only one job can write; multiple jobs can read only if no one is writing.
- `SHAREOPTIONS(2 3)`: Multiple jobs can read concurrently while one job writes.
- `SHAREOPTIONS(3 3)`: Multiple jobs can write concurrently (requires application-level lock coordination or VSAM RLS).

To adjust without deleting:
```jcl
//STEP1    EXEC PGM=IDCAMS
//SYSIN    DD *
  ALTER PROD.KSDS.CUSTOMER SHAREOPTIONS(2 3)
/*
```

### 4. Fix Logic in COBOL Code for Status 92
Ensure the program checks file status flags before issuing OPEN:
```cobol
       IF WS-FILE-IS-OPEN = 'N'
           OPEN I-O CUSTOMER-FILE
           IF WS-CUST-STATUS = '00'
               MOVE 'Y' TO WS-FILE-IS-OPEN
           ELSE
               PERFORM 9900-HANDLE-OPEN-ERROR
           END-IF
       END-IF.
```""",
        "prevention": [
            "Use VSAM Record-Level Sharing (RLS) to allow concurrent updates from both batch and CICS.",
            "Automate CICS file close/open sequences using CA-7 or modern schedulers like Stonebranch before batch execution.",
            "Always verify file status variables immediately after every I/O statement in COBOL.",
            "Never use `DISP=OLD` in batch JCL when `DISP=SHR` satisfies requirements."
        ],
        "references": [
            {"title": "IBM DFSMS Using Data Sets: VSAM Status Codes", "url": "https://www.ibm.com/docs/en/zos/latest?topic=codes-vsam-return"},
            {"title": "IBM CICS TS: File Control status codes and response values", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=files-file-control-responses"},
            {"title": "StackMF Broadcom CA-7 Replacement & Workload Automation", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },

    # -------------------------------------------------------------------------
    # 15. VSAM CI/CA SPLITS & REORG AUTOMATION
    # -------------------------------------------------------------------------
    {
        "slug": "vsam-ci-ca-splits-reorg-idcams",
        "title": "Eliminating Performance Degradation from VSAM KSDS CI/CA Splits: IDCAMS REORG Automation",
        "date": "2026-09-27",
        "category": "CICS & VSAM Architecture",
        "tags": ["VSAM", "KSDS", "CI Splits", "CA Splits", "IDCAMS", "REORG", "FREESPACE"],
        "reading_time": "9 min read",
        "tldr": "High volumes of random inserts into a VSAM KSDS cause Control Interval (CI) and Control Area (CA) splits, leading to severe I/O bottlenecks and disk fragmentation. Learn how to monitor split metrics, calibrate FREESPACE, and automate zero-downtime IDCAMS REORGs.",
        "problem": """Online transactions reading a core customer VSAM KSDS experience response time degradation, jumping from 30ms to over 800ms. Batch processing times double. System monitors report excessive I/O wait times and physical DASD head contention on volumes hosting the VSAM cluster.""",
        "root_cause": """A VSAM KSDS is organized into Control Intervals (CIs) grouped into Control Areas (CAs):
1. **Control Interval (CI) Split**: When a program inserts a record into a CI that lacks sufficient free space, VSAM creates a new CI within the same CA, moves roughly half the records to it, and updates the index. While this takes some CPU and I/O time, records remain within the same cylinder.
2. **Control Area (CA) Split**: When a CI split occurs but there are no remaining free CIs within that Control Area, VSAM must split the entire CA. It allocates a brand-new CA at the physical end of the dataset, moves half the CIs to it, and updates the high-level index.

CA splits require moving megabytes of data across cylinders, causing severe rotational delay, index fragmentation, and serialization bottlenecks across the parallel sysplex.""",
        "solution": """### 1. Analyze CI and CA Splits via IDCAMS LISTCAT
Run an IDCAMS `LISTCAT` report:
```jcl
//STEP1    EXEC PGM=IDCAMS
//SYSPRINT DD SYSOUT=*
//SYSIN    DD *
  LISTCAT ENTRIES('PROD.KSDS.CUSTOMER') ALL
/*
```
Look for:
```text
SPLITS-CI ------------ 14,290
SPLITS-CA -------------- 1,412
FREESPACE-%CI ------------- 0
FREESPACE-%CA ------------- 0
EXCP-COUNT -------- 14,812,094
```
Over 1,400 CA splits indicates massive fragmentation and urgent reorg requirement!

### 2. Calibrate FREESPACE Parameter
When defining the KSDS, provide adequate freespace tailored to the insert rate:
- For uniform random inserts: `FREESPACE(20 20)` reserves 20% free space in each CI and 20% free CIs in each CA.
- For sequential inserts at the end of the file: `FREESPACE(0 0)` is optimal.

### 3. Automated IDCAMS REORG Script
Execute an IDCAMS backup, delete/define, and reload:
```jcl
//REORG    JOB (ACCT),'VSAM REORG',CLASS=A,MSGCLASS=X
//STEP1    EXEC PGM=IDCAMS
//SYSPRINT DD SYSOUT=*
//BACKUP   DD DSN=PROD.KSDS.CUSTOMER.BKUP,DISP=(NEW,CATLG,DELETE),
//            SPACE=(CYL,(100,50),RLSE),UNIT=SYSDA
//SYSIN    DD *
  /* 1. EXPORT/REPRO DATA TO BACKUP */
  REPRO INDATASET('PROD.KSDS.CUSTOMER') -
        OUTDATASET('PROD.KSDS.CUSTOMER.BKUP')

  /* 2. DELETE OLD CLUSTER */
  DELETE 'PROD.KSDS.CUSTOMER' CLUSTER PURGE

  /* 3. REDEFINE WITH OPTIMIZED FREESPACE & BUFFERSPACE */
  DEFINE CLUSTER (NAME('PROD.KSDS.CUSTOMER') -
         CYLINDERS(200 50) -
         RECORDSIZE(250 250) -
         KEYS(16 0) -
         FREESPACE(20 15) -
         SHAREOPTIONS(2 3) -
         BUFFERSPACE(1048576)) -
         DATA (NAME('PROD.KSDS.CUSTOMER.DATA')) -
         INDEX (NAME('PROD.KSDS.CUSTOMER.INDEX'))

  /* 4. REPOPULATE FROM BACKUP */
  REPRO INDATASET('PROD.KSDS.CUSTOMER.BKUP') -
        OUTDATASET('PROD.KSDS.CUSTOMER')
/*
```""",
        "prevention": [
            "Monitor VSAM datasets weekly and trigger automated REORG when `SPLITS-CA > 50`.",
            "Tune `BUFFERSPACE` parameter to allow at least 5 data buffers and 2 index buffers in batch JCL (`AMP=('BUFND=10,BUFNI=5')`).",
            "Place the VSAM Index component on high-speed solid-state or cache-boosted DASD volumes.",
            "Evaluate converting critical high-churn VSAM datasets to IBM DB2 tables for automatic space management."
        ],
        "references": [
            {"title": "IBM DFSMS Access Method Services Commands: DEFINE CLUSTER", "url": "https://www.ibm.com/docs/en/zos/latest?topic=commands-define-cluster"},
            {"title": "IBM Redbooks: VSAM Demystified", "url": "https://www.redbooks.ibm.com/abstracts/sg246105.html"},
            {"title": "StackMF 24/7 Managed Application Maintenance (AMS)", "url": "https://stackmf.com/#maintenance-ams"}
        ]
    },

    # -------------------------------------------------------------------------
    # 16. VSAM RECORD-LEVEL SHARING (RLS) IN SYSPLEX
    # -------------------------------------------------------------------------
    {
        "slug": "vsam-rls-record-level-sharing-sysplex",
        "title": "Implementing VSAM Record-Level Sharing (RLS) for Concurrent Batch and CICS Access",
        "date": "2026-09-27",
        "category": "CICS & VSAM Architecture",
        "tags": ["VSAM", "VSAM RLS", "CICS", "Parallel Sysplex", "SMSVSAM", "Coupling Facility"],
        "reading_time": "10 min read",
        "tldr": "VSAM RLS enables concurrent update access across multiple CICS regions and batch jobs across a Parallel Sysplex without closing files or causing File Status 93 contention. Discover SMSVSAM configuration, Coupling Facility lock structures, and JCL changes.",
        "problem": """An enterprise operating 24/7 banking operations cannot take CICS regions offline to allow nightly batch processing jobs to update core VSAM accounting datasets. Batch jobs attempting to run concurrently fail with File Status 93 or wait indefinitely on dataset enqueues, blocking time-critical transaction feeds.""",
        "root_cause": """Standard VSAM uses operating system file-level enqueues (`SHAREOPTIONS`). When an application opens a file for output, it acquires exclusive serialization for the entire dataset.

To achieve continuous 24/7 operation without database conversion, IBM introduced **VSAM Record-Level Sharing (RLS)**:
- Serialization moves from whole-file enqueues to individual records via the SMSVSAM address space and the Coupling Facility (CF).
- Multiple CICS Application Owning Regions (AORs) and batch jobs across any LPAR in the Parallel Sysplex can update different records in the same KSDS simultaneously without locking each other out.""",
        "solution": """### 1. Verify Storage Class & SMSVSAM Prerequisites
Ensure the Coupling Facility has allocated the lock and cache structures:
- `IGWLOCK00`: The sysplex-wide CF lock structure.
- Assign an SMS Storage Class with a defined cache set name:
```jcl
//STEP1    EXEC PGM=IDCAMS
//SYSIN    DD *
  ALTER PROD.KSDS.CUSTOMER -
        LOG(NONE) -
        BWO(TYPECICS)
/*
```
- `LOG(NONE)`: Non-recoverable (or `LOG(UNDO)` / `LOG(ALL)` for CICS dynamic transaction backout via CICS System Log).

### 2. Update Batch JCL for RLS Mode
To access the dataset in RLS mode in batch jobs, specify `RLS=NRI` (No Read Integrity) or `RLS=CR` (Consistent Read) in the JCL `AMP` parameter:
```jcl
//CUSTFILE DD DSN=PROD.KSDS.CUSTOMER,
//            DISP=SHR,
//            RLS=CR
```
For update operations:
```jcl
//CUSTFILE DD DSN=PROD.KSDS.CUSTOMER,
//            DISP=SHR,
//            RLS=CRE
```

### 3. Update CICS FCT / CSD Definitions
In CICS, update the file definition:
```text
CEDA DEFINE FILE(CUSTFILE) GROUP(FINAPP)
     DSNAME(PROD.KSDS.CUSTOMER)
     RLSACCESS(YES)
     RECORDFORMAT(F)
     STRINGS(20)
```
Install the definition:
```text
CEDA INSTALL FILE(CUSTFILE) GROUP(FINAPP)
```
Now, batch jobs and CICS transactions can run simultaneously with zero lock contention!""",
        "prevention": [
            "Ensure the Coupling Facility `IGWLOCK00` structure is sized adequately to prevent false lock contention.",
            "Use `RLS=CR` for batch read jobs to prevent reading uncommitted 'dirty' records while CICS transactions are in-flight.",
            "Configure Backup-While-Open (`BWO(TYPECICS)`) to allow DFSMSdss backups without closing CICS files.",
            "Monitor SMSVSAM address space performance via `D SMS,SMSVSAM`."
        ],
        "references": [
            {"title": "IBM DFSMS Using Data Sets: VSAM Record-Level Sharing (RLS)", "url": "https://www.ibm.com/docs/en/zos/latest?topic=rls-vsam-record-level-sharing"},
            {"title": "IBM Redbooks: CICS and VSAM Record-Level Sharing", "url": "https://www.redbooks.ibm.com/abstracts/sg245464.html"},
            {"title": "StackMF Modernization Architecture & Sysplex Engineering", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },

    # -------------------------------------------------------------------------
    # 17. Z/OS CONNECT REST API COBOL & CICS
    # -------------------------------------------------------------------------
    {
        "slug": "zos-connect-rest-api-cobol-cics",
        "title": "Modernizing COBOL Copybooks to OpenAPI 3.0 REST APIs using IBM z/OS Connect",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Modernisation", "z/OS Connect", "OpenAPI", "REST API", "COBOL", "CICS"],
        "reading_time": "11 min read",
        "tldr": "Unlock legacy core mainframe assets by exposing COBOL Commareas and CICS Channels/Containers as OpenAPI 3.0 RESTful endpoints with sub-10ms latency using IBM z/OS Connect EE. Say goodbye to brittle screen scraping and middleware gateways.",
        "problem": """Enterprise digital channels (mobile apps, React/Node.js web portals, cloud microservices) require real-time JSON access to core banking logic residing in 30-year-old COBOL/CICS programs. Previous attempts relied on fragile 3270 screen scraping or heavyweight SOAP wrappers that broke under load and incurred immense MIPS costs.""",
        "root_cause": """Core mainframe transactions expect EBCDIC binary structures:
- `DFHCOMMAREA` or CICS Containers formatted with binary integers (`COMP`), packed decimals (`COMP-3`), and padded strings (`PIC X`).
- Modern cloud applications communicate in UTF-8 JSON via HTTP REST.

Translating between these worlds manually requires massive boilerplate code. IBM z/OS Connect Enterprise Edition acts as a lightweight, zIIP-eligible API gateway running inside the z/OS subsystem, transforming JSON payloads directly into binary CICS Commareas without modifying existing COBOL source code.""",
        "solution": """### 1. Define the COBOL Copybook Structure
Take the existing CICS program interface copybook (`INVOICE.CPY`):
```cobol
       01  INVOICE-REQUEST.
           05  REQ-ACCOUNT-ID          PIC X(10).
           05  REQ-ACTION-CODE         PIC X(02).
       01  INVOICE-RESPONSE.
           05  RESP-STATUS-CODE        PIC X(04).
           05  RESP-CUSTOMER-NAME      PIC X(35).
           05  RESP-BALANCE-DUE        PIC S9(7)V99 COMP-3.
           05  RESP-DUE-DATE           PIC X(10).
```

### 2. Generate OpenAPI 3.0 Mapping using z/OS Connect Designer
Using the z/OS Connect Designer tool:
1. Import `INVOICE.CPY` as the request and response data structure.
2. The tool maps:
   - `REQ-ACCOUNT-ID` -> JSON property `"accountId": "string"`
   - `RESP-BALANCE-DUE` -> JSON property `"balanceDue": 1250.75`
3. Map HTTP verbs: `POST /api/v1/invoices` routes to CICS program `INVP01`.

### 3. Deploy the API Package to the z/OS Connect Server
Package the project into a `.aar` (API Archive) and drop it into the server configuration:
```xml
<!-- server.xml -->
<server description="z/OS Connect Production Gateway">
    <featureManager>
        <feature>zosConnect:zosConnect-2.0</feature>
        <feature>zosConnect:cicsService-1.0</feature>
    </featureManager>

    <zosConnect_cicsIpicConnection id="cicsConn"
        host="127.0.0.1"
        port="10443"
        connectionTimeout="5s"/>
</server>
```

### 4. Test the Generated REST Endpoint
From any modern curl or Node.js client:
```bash
curl -X POST https://api.stackmf.bank/api/v1/invoices \
     -H "Content-Type: application/json" \
     -d '{"accountId": "ACC-99214", "actionCode": "IN"}'
```
Response returns within 6 milliseconds in pure JSON:
```json
{
  "statusCode": "0000",
  "customerName": "ACME CORPORATION",
  "balanceDue": 14250.50,
  "dueDate": "2026-10-15"
}
```""",
        "prevention": [
            "Enable zIIP eligibility for z/OS Connect address spaces to execute JSON-to-EBCDIC transformations on zero-MLC specialty engines.",
            "Use CICS Channels and Containers instead of 32KB Commarea limits for new REST API programs.",
            "Enforce JWT / OAuth 2.0 token validation at the z/OS Connect boundary to authenticate microservice callers.",
            "Version all API contracts strictly in Git repositories using modern API-first governance."
        ],
        "references": [
            {"title": "IBM z/OS Connect Enterprise Edition Documentation", "url": "https://www.ibm.com/docs/en/zos-connect/3.0"},
            {"title": "IBM Redbooks: Modernizing Mainframe Applications with REST and APIs", "url": "https://www.redbooks.ibm.com/abstracts/sg248386.html"},
            {"title": "StackMF Mainframe Modernization & Full-Stack Bridge", "url": "https://stackmf.com/#fullstack-bridge"}
        ]
    },

    # -------------------------------------------------------------------------
    # 18. MAINFRAME TO KAFKA CDC EVENT STREAMING
    # -------------------------------------------------------------------------
    {
        "slug": "mainframe-kafka-event-streaming-cdc",
        "title": "Real-Time Mainframe Change Data Capture (CDC) to Apache Kafka: Streaming DB2 & VSAM to Cloud",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Modernisation", "Apache Kafka", "CDC", "DB2", "VSAM", "Cloud Lakehouse"],
        "reading_time": "11 min read",
        "tldr": "Eliminate overnight batch ETL delays by capturing row-level inserts, updates, and deletes from DB2 for z/OS and VSAM log streams and streaming them directly into Apache Kafka, Snowflake, and AWS/GCP with sub-second latency.",
        "problem": """Enterprise cloud data lakes (Snowflake, BigQuery, Databricks) require near real-time updates from core mainframe transaction systems. Traditional overnight batch extract jobs (running SQL unloads or VSAM REPROs) cause high peak MIPS consumption and leave business intelligence systems up to 24 hours out of date.""",
        "root_cause": """Mainframe databases process hundreds of thousands of transactions per second. Re-reading entire tables causes immense DASD I/O and CPU overhead.

The non-intrusive solution is **Change Data Capture (CDC)**:
- DB2 for z/OS writes all committed modifications to its Write-Ahead Log (WAL / active logs).
- VSAM logs writes via CICS forward recovery logs or DFSMS replication logs.
- A specialized CDC engine (such as IBM InfoSphere Data Replication / IIDR or open-source Debezium/Zowe agents) reads the log stream asynchronously without impacting application transaction response times, translates EBCDIC records into Avro or JSON, and produces them to Apache Kafka topics.""",
        "solution": """### 1. Enable DB2 DATA CAPTURE CHANGES
Enable logging of pre- and post-images for target tables:
```sql
ALTER TABLE CUSTOMER_TRANSACTIONS
      DATA CAPTURE CHANGES;
```
This instructs DB2 to record the full before-and-after row images in the active DB2 log rather than just modified column deltas.

### 2. Configure Kafka Connector Pipeline
Deploy an event stream connector consuming the mainframe replication stream:
```json
{
  "name": "mainframe-db2-cdc-source",
  "config": {
    "connector.class": "io.confluent.connect.ibm.db2.Db2SourceConnector",
    "tasks.max": "3",
    "connection.url": "jdbc:db2://zsys1.stackmf.internal:5021/DB2P",
    "connection.user": "CDCUSER",
    "table.whitelist": "BANKING.CUSTOMER_TRANSACTIONS",
    "topic.prefix": "mainframe.prod.",
    "transforms": "unwrap,reroute",
    "transforms.unwrap.type": "io.debezium.transforms.ExtractNewRecordState"
  }
}
```

### 3. Real-Time Cloud Consumer
Downstream cloud microservices or streaming jobs (e.g., Python / Apache Flink / Spark) consume real-time updates instantly:
```python
from kafka import KafkaConsumer
import json

consumer = KafkaConsumer(
    'mainframe.prod.CUSTOMER_TRANSACTIONS',
    bootstrap_servers=['kafka-cluster.stackmf.cloud:9092'],
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    tx = message.value
    print(f"Mainframe Event: Acct={tx['ACCOUNT_ID']}, Amt=${tx['AMOUNT']}, Type={tx['TX_TYPE']}")
```""",
        "prevention": [
            "Size DB2 active log datasets appropriately to prevent log contention during high-churn peaks.",
            "Run CDC log reading on zIIP specialty engines where supported to prevent billable MLC MIPS consumption.",
            "Enforce Apache Avro or Protobuf schemas with schema registries to manage schema evolution between mainframe and cloud.",
            "Implement end-to-end telemetry monitoring Kafka consumer lag to detect network or broker delays."
        ],
        "references": [
            {"title": "IBM InfoSphere Data Replication for Db2 for z/OS", "url": "https://www.ibm.com/docs/en/idr/11.4.0"},
            {"title": "Confluent: Mainframe Event Streaming with Apache Kafka Architecture", "url": "https://www.confluent.io/use-case/mainframe-integration/"},
            {"title": "StackMF Enterprise Mainframe Modernization Services", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },

    # -------------------------------------------------------------------------
    # 19. COBOL & JAVA DUAL-STACK INTEROPERABILITY
    # -------------------------------------------------------------------------
    {
        "slug": "cobol-java-interoperability-zos",
        "title": "Dual-Stack COBOL and Java Interoperability on z/OS using 64-bit IBM Semeru Runtime",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Modernisation", "COBOL", "Java", "z/OS", "zIIP", "Semeru"],
        "reading_time": "10 min read",
        "tldr": "Enterprise COBOL 6.4 allows seamless, bi-directional calling between COBOL and Java in the same address space. Offload compute-intensive business logic, encryption, and machine learning to zIIP specialty engines, saving up to 90% on IBM software charges.",
        "problem": """Enterprises struggle to modernize core business logic written in COBOL while recruiting modern Java/Kotlin developers. Rewriting monolithic COBOL applications from scratch carries massive risk and multi-year delays, while running pure COBOL on general-purpose CPs continues to drive up IBM monthly software licensing charges (MLC).""",
        "root_cause": """Traditionally, COBOL and Java ran in separated environments on z/OS, requiring IPC, MQ queues, or socket calls to exchange data.

In **Enterprise COBOL 6.4** and **IBM Semeru Runtime for z/OS (Java 11/17)**:
- Java and COBOL run inside the **same Language Environment enclave** and share memory.
- A COBOL program can call static Java methods directly, passing parameters without serialization.
- All Java bytecode execution automatically qualifies for **IBM zIIP (System z Integrated Information Processor)** specialty engines, executing at zero IBM software license charge!""",
        "solution": """### 1. Write the Java Service Class
Create a standard Java class compiled for the IBM Semeru JVM on z/OS:
```java
package com.stackmf.finance;

import java.math.BigDecimal;

public class FraudRiskCalculator {
    public static double computeScore(String accountId, double transactionAmount) {
        // Advanced AI/ML or statistical fraud scoring
        if (transactionAmount > 10000.0 && accountId.startsWith("RISK")) {
            return 98.5; // High Risk
        }
        return 12.0; // Safe
    }
}
```

### 2. Call Java Directly from Enterprise COBOL 6.4
COBOL 6.4 includes native Java interoperability syntax:
```cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. CHECKTX.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01  WS-ACCT-ID           PIC X(10) VALUE 'RISK-40912'.
       01  WS-AMOUNT            COMP-2    VALUE 15420.00.
       01  WS-FRAUD-SCORE       COMP-2.

       PROCEDURE DIVISION.
           DISPLAY 'Invoking Java Fraud Scoring Engine on zIIP...'
           
      * Native direct invocation of Java method
           CALL 'Java.com.stackmf.finance.FraudRiskCalculator.computeScore'
                USING BY VALUE WS-ACCT-ID
                      BY VALUE WS-AMOUNT
                RETURNING WS-FRAUD-SCORE.

           IF WS-FRAUD-SCORE > 85.0
               DISPLAY 'Alert: Transaction Blocked! Risk Score: ' WS-FRAUD-SCORE
           ELSE
               DISPLAY 'Transaction Approved.'
           END-IF.
           GOBACK.
```

### 3. Compile and Link with JNI Support
Compile with `JAVAPROXY` and link with the z/OS Java native interface:
```jcl
//COBSTEP EXEC PGM=IGYCRCTL,
//  PARM='OPT(2),ARCH(14),JAVAPROXY(ALL),LP(64)'
//SYSLIB   DD DSN=CEE.SCEELKED,DISP=SHR
//         DD DSN=SYS1.JAVA.LIB,DISP=SHR
```""",
        "prevention": [
            "Ensure zIIP capacity is monitored to prevent Java threads from overflowing onto billable general-purpose engines.",
            "Use 64-bit addressing (`LP(64)`) to allocate large Java heaps without constraining 31-bit below-the-bar storage.",
            "Pass primitive datatypes by value across the COBOL/Java boundary for maximum performance.",
            "Store compiled `.class` and `.jar` artifacts in the z/OS UNIX System Services (USS) hierarchical filesystem."
        ],
        "references": [
            {"title": "IBM Enterprise COBOL for z/OS 6.4 Programming Guide: Interoperability with Java", "url": "https://www.ibm.com/docs/en/cobol-zos/6.4?topic=guide-interoperability-java"},
            {"title": "IBM Semeru Runtime Certified Edition for z/OS", "url": "https://www.ibm.com/products/semeru-runtime-zos"},
            {"title": "StackMF Mainframe Full-Stack Developer Hiring Pods", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },

    # -------------------------------------------------------------------------
    # 20. REPLACING ENDEVOR WITH GIT & ZOWE
    # -------------------------------------------------------------------------
    {
        "slug": "replacing-broadcom-endevor-with-git-zowe",
        "title": "Migrating from Broadcom Endevor to Git & Modern CI/CD using Zowe CLI and IBM DBB",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["Endevor", "DevOps", "Broadcom Replacement", "Git", "Zowe CLI", "IBM DBB"],
        "reading_time": "12 min read",
        "tldr": "Eliminate escalating Broadcom Endevor licensing fees by migrating your mainframe source code inventory, components, and processors to Git repositories orchestrated with Zowe CLI, GitHub Actions, and IBM Dependency Based Build (DBB).",
        "problem": """Enterprises face 150% to 300% price increases during Broadcom Endevor contract renewals. Modern developers find Endevor's green-screen ISPF package promotion workflow archaic and siloed, while enterprise CI/CD teams cannot integrate mainframe deployments into standard GitHub Enterprise or GitLab pipelines.""",
        "root_cause": """Broadcom Endevor manages mainframe source code in a proprietary stage-and-element lifecycle (Dev -> Test -> QA -> Prod) bound to PDS datasets.

Modern Git-native mainframe engineering replaces this closed model:
- **Git** becomes the single source of truth for all COBOL, Copybook, BMS, and JCL assets.
- **IBM Dependency Based Build (DBB)** provides intelligent dependency scanning (identifying exactly which programs must be recompiled when a copybook changes).
- **Zowe CLI & GitHub Actions** automate building, compiling, and deploying load modules to z/OS through REST APIs, completely deprecating Endevor.""",
        "solution": """### 1. Extract Elements and History from Endevor
Use Endevor's batch utility (`BC1PNMTR` / `CONWRITE`) to export source elements, copybooks, and historical levels to z/OS UNIX files:
```jcl
//EXPORT   EXEC PGM=NDVRC1,PARM='CONWRITE'
//SYSPRINT DD SYSOUT=*
//OUTPUT   DD PATH='/u/migration/repo/cobol/MOD01.cbl',
//            PATHOPTS=(OWRONLY,OCREAT,OTRUNC),
//            PATHMODE=(SIRWXU,SIRWXG)
//SYSIN    DD *
  WRITE ELEMENT MOD01
        FROM ENVIRONMENT PROD SYSTEM BILLING SUBSYSTEM CORE
        TYPE COBOL STAGE P
        TO DDNAME OUTPUT.
/*
```

### 2. Organize Git Repository Structure
Structure your enterprise Git repository:
```text
├── cobol/
│   ├── ACCNTREC.cbl
│   └── INVP01.cbl
├── copybook/
│   ├── INVOICE.cpy
│   └── COMMREG.cpy
├── jcl/
│   └── RUNINVOICE.jcl
├── build/
│   └── build.groovy (IBM DBB Build Script)
└── .github/workflows/
    └── zos-build.yml
```

### 3. Automate Deployments with GitHub Actions & Zowe CLI
In `.github/workflows/zos-build.yml`:
```yaml
name: z/OS Mainframe CI/CD Pipeline
on: [push, pull_request]

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Setup Node & Zowe CLI
        uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Zowe CLI
        run: npm install -g @zowe/cli

      - name: Submit DBB Impact Build on z/OS
        env:
          ZOWE_OPT_HOST: ${{ secrets.ZOS_HOST }}
          ZOWE_OPT_USER: ${{ secrets.ZOS_USER }}
          ZOWE_OPT_PASSWORD: ${{ secrets.ZOS_PASS }}
        run: |
          zowe zos-uss issue ssh-command "groovyz /u/dbb/build.groovy -r /u/repos/stackmf"
```
Developers gain instantaneous branch-based development, automated pull requests, and automated testing—all while zeroing out Broadcom software fees!""",
        "prevention": [
            "Maintain strict branch protection rules on `main` to replicate Endevor's production approval controls.",
            "Use IBM DBB metadata store (DBB Metastore) to record build footprints and dependency maps.",
            "Train mainframe teams on Git branching models (Trunk-based or GitFlow) before decommissioning Endevor.",
            "Leverage StackMF's turnkey Broadcom Endevor Migration Framework for guaranteed zero-downtime cutover."
        ],
        "references": [
            {"title": "Open Mainframe Project: Zowe CLI Documentation", "url": "https://docs.zowe.org/stable/user-guide/cli-usingcli"},
            {"title": "IBM Dependency Based Build (DBB) Knowledge Center", "url": "https://www.ibm.com/docs/en/dbb/latest"},
            {"title": "StackMF Turnkey Broadcom Product Replacement Hub", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },

    # -------------------------------------------------------------------------
    # 21. AUTOMATING CA-7 MIGRATION TO STONEBRANCH / CONTROL-M
    # -------------------------------------------------------------------------
    {
        "slug": "automating-ca7-migration-to-stonebranch-controlm",
        "title": "Broadcom CA-7 / CA-11 Decoupling: Migrating 20,000+ JCL Batch Schedules to Stonebranch or Control-M",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["CA-7", "CA-11", "Stonebranch", "Control-M", "Broadcom Replacement", "JCL"],
        "reading_time": "12 min read",
        "tldr": "Escape exorbitant Broadcom Workload Automation (CA-7 / CA-11) renewal hikes. Discover automated parsing of BROWSE databases, translating predecessor/successor trigger nets, and establishing hybrid cloud orchestration with Stonebranch UAC or BMC Control-M.",
        "problem": """Organizations running thousands of critical overnight batch workloads face massive license price hikes for Broadcom CA-7 (Workload Automation) and CA-11 (Restart/Rerun management). Operations teams are locked into 3270 green-screen panels, unable to trigger batch jobs natively from cloud events or orchestrate hybrid jobs across AWS, Azure, and z/OS.""",
        "root_cause": """CA-7 schedules are locked inside proprietary VSAM databases (`U7VOL` / `U7QUEUE`):
- Complex trigger chains: Job triggers (`SCHID`), dataset triggers (`DSN`), network dependencies, manual hold requirements, and calendar base definitions.
- Manual conversion of 20,000+ jobs would take years and introduce immense operational failure risk.

By using automated parsing utilities, CA-7 database definitions can be extracted, translated into vendor-neutral JSON or DAG structures, and imported into modern automation platforms like **Stonebranch Universal Automation Center (UAC)** or **BMC Control-M for z/OS** with automated regression verification.""",
        "solution": """### 1. Extract CA-7 Database via BATCH Terminal Interface (BTI)
Execute CA-7 utility `CAL2JCL` or BTI to dump job definitions, triggers, and requirements:
```jcl
//DUMPCA7  EXEC PGM=CA07BTI
//SYSPRINT DD SYSOUT=*
//SYSIN    DD *
/LOGON MASTER
LJOB,JOB=*,LIST=ALL
LDSN,DSN=*
LPRRN,JOB=*
/LOGOFF
/*
```

### 2. Automated Translation to Stonebranch Universal Tasks
The StackMF automated parser processes the raw CA-7 output and converts triggers into Stonebranch Task Definitions:
```json
{
  "taskType": "ZOS_JOB",
  "name": "BILLING_NIGHTLY_JOB01",
  "jclMember": "PROD.JCL.CNTL(BILL010)",
  "system": "LPAR1",
  "triggers": [
    {
      "type": "DATASET_TRIGGER",
      "datasetName": "PROD.TRANSACTIONS.FINAL",
      "condition": "CLOSED_SUCCESSFULLY"
    }
  ],
  "successConditions": [
    { "maxReturnCode": 4 }
  ],
  "dependencies": [
    { "task": "GL_POSTING_JOB", "relationship": "SUCCESSOR" }
  ]
}
```

### 3. Replace CA-11 Automated Restart Logic
CA-11 requires proprietary step insertion (`//STEP1 EXEC PGM=U11RMS`). In modern schedulers, this is replaced by native step-level restart capabilities:
- Inspect condition codes natively.
- Dynamically restart at any failed JCL step without modifying original production JCL!""",
        "prevention": [
            "Run parallel schedule verification for 30 consecutive business days before cutting off CA-7.",
            "Decouple hardcoded dataset dependencies into event-driven pub/sub signals.",
            "Implement role-based modern web dashboard access for operations personnel.",
            "Engage StackMF for our automated CA-7 migration accelerator to guarantee fixed-timeline, zero-loss cutover."
        ],
        "references": [
            {"title": "Stonebranch: Mainframe Modernization and CA-7 Replacement Guide", "url": "https://www.stonebranch.com/solutions/mainframe-modernization"},
            {"title": "BMC Control-M for z/OS Automation Solutions", "url": "https://www.bmc.com/it-solutions/control-m-zos.html"},
            {"title": "StackMF Broadcom Savings & Replacement ROI Calculator", "url": "https://stackmf.com/#tco-calculator"}
        ]
    },

    # -------------------------------------------------------------------------
    # 22. REXX AUTOMATION FOR TSO/E & ISPF UTILITIES
    # -------------------------------------------------------------------------
    {
        "slug": "rexx-automation-ispf-tso-utilities",
        "title": "Building Enterprise REXX Automation: Scripting TSO/E, ISPF Panels, and SDSF Job Parsing",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["REXX", "TSO/E", "ISPF", "SDSF", "Automation", "Batch Monitoring"],
        "reading_time": "9 min read",
        "tldr": "REXX is the scripting powerhouse of z/OS. Learn how to write robust REXX scripts that interact with TSO/E, display custom ISPF panels, and programmatically parse SDSF batch job spool logs to trap production errors automatically without expensive 3rd party tools.",
        "problem": """Systems operators and developers spend hours manually logging into TSO/ISPF, typing SDSF commands, finding failed batch jobs, and manually copying CEEDUMP spools. When production incidents strike, human latency in finding error messages delays Mean Time to Resolution (MTTR).""",
        "root_cause": """While mainframe operational tools are robust, manual interaction through 3270 terminals creates bottlenecks.

REXX (Restructured Extended Executor) natively interfaces with:
- **TSO/E Command Processor**: Issuing dataset allocations, deletes, and catalog searches.
- **ISPF Dialog Manager**: Displaying dynamic user input panels, tables, and popup menus.
- **ISFEXEC (SDSF Host API)**: Programmatically querying the JES2/JES3 input/output spools, filtering by jobname, extracting return codes, and alerting teams via emails or webhook calls.""",
        "solution": """### 1. Build an Automated SDSF Job Parser in REXX
This script queries SDSF for any job ending with ABEND or RC > 4 in the past 2 hours:
```rexx
/* REXX - SDSF BATCH ERROR MONITOR */
Address ISPEXEC
rc = isfcalls('ON')

/* Set SDSF filters */
ISFFILTER = "RETCODE EQ ABEND* OR RETCODE GT 4"
ISFPREFIX = "PROD*"

/* Access the SDSF Status Display */
Address SDSF "ISFEXEC ST"

If rc /= 0 Then Do
  Say "SDSF Query Failed with RC="rc
  Exit 8
End

Say "Found "isfrows" failing jobs in queue."

Do i = 1 To isfrows
  Say "Job: " JNAME.i " ID: " JOBID.i " Return Code: " RETCODE.i
  
  /* Read Spool Datasets for the Failing Job */
  Address SDSF "ISFACT ST TOKEN('"TOKEN.i"') PARM(NP ?)"
  
  Do j = 1 To isfrows
    If DSNAM.j = "SYSPRINT" | DSNAM.j = "CEEDUMP" Then Do
      Address SDSF "ISFBROWSE ST TOKEN('"TOKEN.j"')"
      Do k = 1 To isfbrowse.0
        If Pos("SYSTEM COMPLETION CODE", isfbrowse.k) > 0 Then
          Say "  >>> Root Cause: " isfbrowse.k
      End
    End
  End
End

rc = isfcalls('OFF')
Exit 0
```

### 2. Invoke REXX in Batch JCL
Run the automation script unattended in scheduled batch:
```jcl
//REXXJOB  JOB (ACCT),'REXX MONITOR',CLASS=A,MSGCLASS=X
//STEP1    EXEC PGM=IKJEFT01
//SYSPROC  DD DSN=PROD.REXX.EXEC,DISP=SHR
//SYSTSPRT DD SYSOUT=*
//SYSTSIN  DD *
  EXEC 'PROD.REXX.EXEC(SDSFMON)'
/*
```""",
        "prevention": [
            "Use REXX stem variables (`STEM.0`) for clean memory cleanup when processing large lists.",
            "Always include `SIGNAL ON SYNTAX` and `SIGNAL ON ERROR` for resilient enterprise error handling.",
            "Combine REXX with z/OS UNIX `cURL` commands to post incident alerts directly into Slack or Microsoft Teams.",
            "Store shared enterprise REXX utilities in common `SYSPROC` or `SYSEXEC` concatenations."
        ],
        "references": [
            {"title": "IBM TSO/E REXX Reference (SA22-7790)", "url": "https://www.ibm.com/docs/en/zos/latest?topic=rexx-tsoe-reference"},
            {"title": "IBM SDSF Operation and Customization: Using SDSF with REXX", "url": "https://www.ibm.com/docs/en/zos/latest?topic=rexx-using-sdsf-tsoe"},
            {"title": "StackMF Mainframe Application Development & Staffing", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },

    # -------------------------------------------------------------------------
    # 23. TELON TO CICS BMS SCREEN MIGRATION
    # -------------------------------------------------------------------------
    {
        "slug": "telon-screen-generator-to-cics-bms-migration",
        "title": "De-supporting CA-Telon: Reverse Engineering Generated COBOL Screens into Pure CICS BMS Maps",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Telon", "CA-Telon", "CICS BMS", "COBOL", "Modernisation", "Broadcom Replacement"],
        "reading_time": "11 min read",
        "tldr": "CA-Telon is a legacy 4GL application generator that produces obfuscated COBOL and proprietary runtime dependencies. Discover strategies to de-support Telon, reverse-engineer screen formats into pure CICS Basic Mapping Support (BMS) or modern React front-ends.",
        "problem": """An enterprise relies on hundreds of mission-critical customer service screens generated in the 1990s using CA-Telon. Broadcom support for Telon is costly and specialized skills are nearly extinct. When developers need to update a screen or comply with accessibility guidelines, they find the underlying COBOL code heavily obscured by Telon macro expansions and runtime drivers.""",
        "root_cause": """CA-Telon generated COBOL applications rely on proprietary runtime routines:
1. **Telon Driver Architecture**: Rather than calling standard CICS `RECEIVE MAP` and `SEND MAP` commands directly, Telon programs delegate execution to proprietary runtime modules (e.g., `TLNMAIN`, `TLNCICS`).
2. **Proprietary TDF Data Dictionaries**: Application logic, field validations, and screen transitions are trapped inside proprietary Telon Development Facility (TDF) files.
3. **Macro Obfuscation**: The emitted COBOL contains hundreds of repetitive generated labels, cryptic working-storage copybooks (`TLNPCOMM`), and opaque internal pointer arrays that cannot be easily maintained by standard COBOL engineers.""",
        "solution": """### 1. Extract Screen Coordinates from Telon Panel Definitions
Export the screen panel layout from the Telon catalog or capture the 3270 datastream to extract literal labels, input fields, attributes (protect, numeric, bright), and cursor positions.

### 2. Generate Standard CICS BMS Macro Definition
Convert the extracted panel into pure, vendor-neutral CICS Basic Mapping Support (BMS) assembler macros:
```assembler
* CICS BMS MAPSET DEFINITION - DECOUPLING FROM TELON
CUSTSET  DFHMSD TYPE=&SYSPARM,MODE=INOUT,LANG=COBOL,                   X
               STORAGE=AUTO,TIOAPFX=YES
CUSTMAP  DFHMDI SIZE=(24,80),CTRL=(FREEKB,FRSET)
         DFHMDF POS=(1,28),ATTRB=(ASKIP,BRT),LENGTH=24,               X
               INITIAL='CUSTOMER INQUIRY SYSTEM'
         DFHMDF POS=(4,2),ATTRB=(ASKIP,NORM),LENGTH=12,                X
               INITIAL='ACCOUNT NO:'
ACCTIN   DFHMDF POS=(4,15),ATTRB=(UNPROT,NUM,IC),LENGTH=10
         DFHMDF POS=(4,26),ATTRB=(ASKIP),LENGTH=1
         DFHMDF POS=(6,2),ATTRB=(ASKIP,NORM),LENGTH=12,                X
               INITIAL='CUST NAME :'
NAMEIN   DFHMDF POS=(6,15),ATTRB=(ASKIP,BRT),LENGTH=30
CUSTSET  DFHMSD TYPE=FINAL
         END
```

### 3. Replace Telon Runtime Calls with Native CICS Commands
In the COBOL program, replace the Telon driver invocation with native CICS statements:
```cobol
      * NATIVE CICS RECEIVE & SEND (NO TELON LICENSES REQUIRED)
       EXEC CICS RECEIVE
                 MAP('CUSTMAP')
                 MAPSET('CUSTSET')
                 INTO(CUSTMAPI)
       END-EXEC.

       MOVE CUST-NAME TO NAMEINO.

       EXEC CICS SEND
                 MAP('CUSTMAP')
                 MAPSET('CUSTSET')
                 FROM(CUSTMAPO)
                 ERASE
       END-EXEC.
```

### 4. Alternative: Direct Bridge to Modern Web (React / Vue)
For enterprises looking beyond green-screens, StackMF provides automated converters that translate BMS/Telon field layouts directly into JSON schemas and React UI component libraries!""",
        "prevention": [
            "De-license CA-Telon runtime modules from CICS startup load libraries to eliminate recurrent fees.",
            "Adopt modern API-first architectures using z/OS Connect rather than generating new 3270 screens.",
            "Preserve original business validation rules when extracting logic from Telon generated COBOL.",
            "Partner with StackMF's modernization pods to automate large-scale Telon de-supporting."
        ],
        "references": [
            {"title": "IBM CICS TS: Creating and Using BMS Maps", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=bms-basic-mapping-support"},
            {"title": "Broadcom Support: CA Telon Product Decommissioning Advisory", "url": "https://support.broadcom.com"},
            {"title": "StackMF Enterprise Broadcom Replacement Program", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },

    # -------------------------------------------------------------------------
    # 24. CHANGEMAN ZMF PACKAGE PROMOTION AUDIT RC=08
    # -------------------------------------------------------------------------
    {
        "slug": "serena-changeman-zmf-promotion-freeze-troubleshooting",
        "title": "Resolving Serena / Micro Focus ChangeMan ZMF Package Promotion Freezes and Audit RC 08",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["ChangeMan", "ChangeMan ZMF", "DevOps", "Audit RC 08", "ISPF", "COBOL Staging"],
        "reading_time": "10 min read",
        "tldr": "ChangeMan ZMF package promotions fail when the automated Audit step returns Return Code 08 due to out-of-synch copybooks, missing components, or concurrent change collisions. Learn how to parse the Audit Report and resolve staging discrepancies.",
        "problem": """A developer attempts to promote a critical bugfix package (`CHG0004921`) from Test to Quality Assurance in ChangeMan ZMF. The promotion freezes, status changes to `REJ` (Rejected), and the ChangeMan audit step aborts:
```text
CMN3400I AUDIT STARTED FOR PACKAGE CHG0004921
CMN3412E COMPONENT MODPAY01 OUT OF SYNCH WITH BASELINE COPYBOOK CPYREC1
CMN3499I AUDIT FINISHED WITH HIGHEST RETURN CODE = 08
```
Release managers block the deployment, threatening release cutoff deadlines.""",
        "root_cause": """Micro Focus / Serena ChangeMan ZMF enforces strict release integrity through its automated Audit facility:
1. **Out-of-Synch Copybooks**: Program `MODPAY01` was compiled in the staging library against a copybook version that differs from the one in the baseline or another active concurrent package.
2. **Missing Component Dependencies**: A newly introduced subroutine or DB2 DBRM was staged, but the corresponding package component list omitted the Link-Edit control card or bind member.
3. **Double-Book Collisions**: Another developer checked out the same copybook or program into a different active package without synchronization, creating an uncoordinated change conflict.""",
        "solution": """### 1. View the Detailed ChangeMan Audit Report
In ISPF ChangeMan ZMF:
1. Select option `1` (Package) -> Option `A` (Audit).
2. Browse the `AUDIT REPORT` spool output.
3. Search for all occurrences of severity `E` (Error) or `RC=08`:
```text
*** ERROR *** COMPONENT: CPYREC1 TYPE: COPY
  STAGED FINGERPRINT DOES NOT MATCH BASELINE LEVEL 003.
  PACKAGE CHG0004880 HAS CONCURRENT HOLD ON THIS ELEMENT.
```

### 2. Synchronize Components in the Staging Library
If concurrent package `CHG0004880` already promoted an updated version of `CPYREC1`:
1. Re-copy the updated copybook from baseline into your package:
   ChangeMan Option `1` -> Option `2` (Copy).
2. Re-stage (recompile) the affected COBOL program:
   ChangeMan Option `1` -> Option `3` (Stage) -> Select `MODPAY01`.
3. Verify that the compile listing confirms it pulled the latest copybook generation.

### 3. Re-run Package Audit
Navigate to Option `1.A` and re-run Audit. Once the log reads:
```text
CMN3499I AUDIT FINISHED WITH HIGHEST RETURN CODE = 00
```
The package unlocks and promotion to QA or Production proceeds immediately!""",
        "prevention": [
            "Always run ChangeMan Audit in the developer's development stage before requesting promotion.",
            "Establish cross-package notification alerts when multiple engineers check out components from the same subsystem.",
            "Ensure copybooks are staged and audited prior to staging dependent COBOL programs.",
            "Consider migrating from ChangeMan to Git with modern automated CI/CD for branch-based conflict resolution."
        ],
        "references": [
            {"title": "OpenText / Micro Focus ChangeMan ZMF Documentation", "url": "https://www.microfocus.com/en-us/products/changeman-zmf/overview"},
            {"title": "IBM Redbooks: Modern Mainframe DevOps and Source Control", "url": "https://www.redbooks.ibm.com/abstracts/sg248350.html"},
            {"title": "StackMF Modernization Bridge: Migrating ChangeMan to Git", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },

    # -------------------------------------------------------------------------
    # 25. OPTIMIZING 4HRA WLM BATCH WINDOW COMPRESSION
    # -------------------------------------------------------------------------
    {
        "slug": "optimizing-4hra-wlm-batch-compression",
        "title": "Slashing IBM MLC / WLM Rolling 4-Hour Average (4HRA) through Compiler Optimization & Batch Tuning",
        "date": "2026-09-27",
        "category": "DB2 SQL & Performance",
        "tags": ["Performance", "4HRA", "WLM", "COBOL 6.x", "DFSORT", "MIPS Reduction"],
        "reading_time": "12 min read",
        "tldr": "IBM Monthly License Charges (MLC) are dictated by peak Rolling 4-Hour Average (4HRA) MSU consumption. Discover how to compress your batch processing window by 35% through Enterprise COBOL OPT(3)/ARCH(14), DFSORT memory tuning, and WLM batch cap smoothing.",
        "problem": """The enterprise receives an astronomical monthly invoice for IBM z/OS software (CICS, DB2, z/OS base, COBOL). The Sub-Capacity Reporting Tool (SCRT) indicates that peak billable MSUs spiked between 01:00 AM and 04:00 AM during overnight batch processing, when dozens of heavy batch jobs ran simultaneously and consumed 100% of LPAR capacity.""",
        "root_cause": """IBM sub-capacity pricing bills customers based on the single highest peak of the Rolling 4-Hour Average (4HRA) across the entire month.
- Running un-optimized COBOL (compiled with `OPT(0)` or ancient `OS/390` compilers) burns 20-40% unnecessary CPU cycles per transaction.
- Inefficient DFSORT parameters force sort steps to spill gigabytes to disk work datasets (`SORTWKnn`), stalling CPUs waiting on I/O.
- Running dozens of CPU-hungry batch jobs concurrently during the peak window pushes the 4HRA calculation to astronomical heights.""",
        "solution": """### 1. Upgrade to Enterprise COBOL 6.4 with OPT(3) & ARCH(14)
The modern IBM Enterprise COBOL compiler leverages z16/z15 vector processing instructions:
```jcl
//COBSTEP EXEC PGM=IGYCRCTL,
//  PARM='OPT(3),ARCH(14),HGPR(PRESERVE),TUNE(14),INLINE'
```
- `OPT(3)`: Extreme code generation optimization, register allocation, and dead-code removal.
- `ARCH(14)`: Exploits SIMD vector instructions on IBM z16 hardware for packed decimal math, accelerating COMP-3 calculations up to 3x!

### 2. Tune DFSORT / SyncSort Memory Objects
Eliminate physical disk I/O in sorting by allowing DFSORT to utilize 64-bit storage and memory objects:
```jcl
//DFSPARM  DD *
  OPTION MOSIZE=MAX,
         HIPRMAX=OPTIMAL,
         DYNALLOC=(SYSDA,8),
         SDB=LARGE
/*
```
Sort steps that previously took 40 minutes finish in under 6 minutes entirely in memory.

### 3. WLM Batch Capping and Schedule Smoothing
In the z/OS Workload Manager (WLM):
1. Assign batch jobs to a secondary service class with `DISCRETIONARY` or lower velocity goals.
2. Stagger batch job launches in CA-7 or Stonebranch so CPU-intensive extraction jobs do not overlap.
3. Configure WLM Defined Capacity and Group Capacity Limits to smoothly throttle batch execution without incurring higher billing tiers.""",
        "prevention": [
            "Recompile top 20 CPU-consuming COBOL batch programs using modern `OPT(3)` and `ARCH(14)`.",
            "Audit SCRT reports monthly to track peak 4HRA hours and identify offending job names.",
            "Use DFSORT memory objects (`MOSIZE=MAX`) to avoid disk spill in high-volume sorts.",
            "Engage StackMF for a dedicated 4HRA MIPS Reduction Assessment to cut IBM licensing costs up to 30%."
        ],
        "references": [
            {"title": "IBM Sub-Capacity Reporting Tool (SCRT) User Guide", "url": "https://www.ibm.com/docs/en/zos/latest?topic=reporting-scrt-overview"},
            {"title": "IBM Enterprise COBOL for z/OS 6.4 Performance Tuning Guide", "url": "https://www.ibm.com/docs/en/cobol-zos/6.4?topic=tuning-performance"},
            {"title": "StackMF 24/7 Managed Application Maintenance & AMS", "url": "https://stackmf.com/#maintenance-ams"}
        ]
    }
]
