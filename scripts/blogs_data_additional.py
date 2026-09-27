"""
blogs_data_additional.py - 50 Additional Enterprise Mainframe Knowledge Base Articles
Authored for StackMF Technologies LLP (stackmf.com)

Contains:
- 25 Articles on Zowe, IDz, EZT to IMU conversion, VSCode Zowe plugin, Modern DevOps
- 25 Articles on COBOL, DB2, CICS, VSAM, IMS DB/DC, CA-7, Telon, REXX, Endevor, ChangeMan, ABENDs & Performance
"""

ADDITIONAL_ARTICLES = [
    # =========================================================================
    # PART 1: ZOWE, IDZ, EZT TO IMU CONVERSION, VSCODE ZOWE PLUGIN (25 ARTICLES)
    # =========================================================================
    {
        "slug": "ezt-to-imu-automated-migration-guide",
        "title": "Migrating CA-Easytrieve Plus to COBOL using IBM Migration Utility (IMU / FSCCL1)",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Easytrieve", "IBM Migration Utility", "IMU", "COBOL", "Broadcom Replacement", "FSCCL1"],
        "reading_time": "11 min read",
        "tldr": "Eliminate expensive Broadcom Easytrieve Plus software licenses by converting legacy EZT programs into standard Enterprise COBOL using IBM Migration Utility (IMU). Learn how to set up the FSCCL1 translator step, configure EZPARAMS, and verify bit-for-bit output parity.",
        "problem": """Enterprises paying millions annually in Broadcom software renewals discover hundreds of legacy CA-Easytrieve Plus programs embedded in critical nightly batch extraction pipelines. Because Easytrieve is an interpreted or proprietary-compiled language, removing the Broadcom runtime causes jobs executing PGM=EZTPA00 to fail with ABEND S806 (Module Not Found).""",
        "root_cause": """CA-Easytrieve Plus relies on proprietary macros, file control tables, and runtime dynamic link modules (`EZTPA00`, `EZTPX01`).
IBM Migration Utility (IMU / product 5655-MGM) provides a transparent source-to-source compiler:
- IMU preprocessor `FSCCL1` translates Easytrieve statements (`JOB INPUT`, `PRINT`, `REPORT`) into standard Enterprise COBOL source code.
- The emitted COBOL is compiled with `IGYCRCTL` and linked into standard z/OS executable load modules.
- Jobs run at native machine speed, completely bypassing Easytrieve runtime licenses while slashing CPU consumption up to 25%.""",
        "solution": """### 1. Configure the IMU Translation JCL Step
Replace the legacy `EXEC PGM=EZTPA00` with the standard IMU conversion cataloged procedure (`FSCASAP`):
```jcl
//STEP1    EXEC PGM=FSCCL1,
//  PARM='LIST,SOURCE,NODECK,NOTEST,NOMAP,FLAG(I)'
//STEPLIB  DD DSN=SYS1.IMU.SFSCLLMD,DISP=SHR
//SYSIN    DD DSN=PROD.EZT.SRCLIB(REPORT01),DISP=SHR
//SYSOUT   DD SYSOUT=*
//FSCCOBOL DD DSN=&&COBSRCE,DISP=(NEW,PASS),
//            SPACE=(CYL,(5,2)),UNIT=SYSDA,
//            DCB=(RECFM=FB,LRECL=80,BLKSIZE=27920)
//FSCDMSG  DD SYSOUT=*
//SYSERRS  DD SYSOUT=*
```

### 2. Configure EZPARAMS Translation Rules
Customize the IMU translation table (`EZPARAMS`) to ensure compatibility:
```text
* IMU EZPARAMS CONFIGURATION
COLLSEQ=EBCDIC
DOWHILE=NATIVE
EASYTRAN=YES
SQLMODE=BIND
PAGESIZE=060
LINESIZE=132
AUTOCB=YES
```

### 3. Compile and Link the Emitted COBOL
Pass `&&COBSRCE` to standard Enterprise COBOL compiler:
```jcl
//COBSTEP  EXEC PGM=IGYCRCTL,PARM='OPT(2),ARCH(14)'
//SYSIN    DD DSN=&&COBSRCE,DISP=(OLD,DELETE)
//SYSLIN   DD DSN=&&LOADSET,DISP=(MOD,PASS),SPACE=(CYL,(2,1))
```

### 4. Execute the Converted Native Load Module
Run the compiled application without any Broadcom software active:
```jcl
//RUNSTEP  EXEC PGM=REPORT01
//STEPLIB  DD DSN=PROD.CONVERTED.LOADLIB,DISP=SHR
//SYSUT1   DD DSN=PROD.INVOICE.INPUT,DISP=SHR
//SYSPRINT DD SYSOUT=*
```""",
        "prevention": [
            "Run automated parallel runs for 3 cycles comparing the legacy Easytrieve output dataset with IMU-generated COBOL output byte-by-byte using SuperC (`ISRSUPC`).",
            "Establish automated Git/Zowe CI/CD pipelines to compile new reporting logic directly in COBOL.",
            "Eliminate unneeded Easytrieve temporary WORK files by leveraging COBOL internal tables or memory arrays.",
            "De-license Broadcom Easytrieve libraries from system LNKLST once conversion passes audit."
        ],
        "references": [
            {"title": "IBM Migration Utility for z/OS User's Guide (SC27-8777)", "url": "https://www.ibm.com/docs/en/imu/5.1.0"},
            {"title": "StackMF Broadcom Product Replacement & License Elimination", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },
    {
        "slug": "ezt-file-status-abends-in-imu-conversion",
        "title": "Resolving File Status and Arithmetic Truncation Mismatches in Easytrieve-to-IMU Conversions",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Easytrieve", "IMU", "File Status", "COBOL", "Truncation", "FSCCL1"],
        "reading_time": "9 min read",
        "tldr": "When converting Easytrieve to COBOL via IMU, differences in default arithmetic rounding, file status evaluations, and binary data alignment can cause S0C7 ABENDs or unexpected calculations. Learn how to tune IMU compiler options to ensure exact bitwise equivalence.",
        "problem": """After migrating an Easytrieve reporting program to COBOL using IBM Migration Utility, the new load module terminates in batch with ABEND S0C7 at an arithmetic instruction, or writes different calculated tax totals on page footers compared to the legacy Easytrieve report.""",
        "root_cause": """Easytrieve Plus and Enterprise COBOL handle data semantics differently:
1. **Arithmetic Precision & Truncation**: Easytrieve defaults to floating-point or dynamic decimal scaling during intermediate calculations, whereas Enterprise COBOL adheres strictly to fixed-point intermediate rules (`ARITH(EXTEND)` vs `ARITH(COMPAT)`).
2. **File Status Leniency**: In Easytrieve, reading past End-of-File or encountering minor record length discrepancies often sets `EOF` flags without raising exceptions, whereas standard COBOL file handlers enforce strict `FILE STATUS` checks.""",
        "solution": """### 1. Enable Native Truncation Rules in EZPARAMS
Set `TRUNC=OPT` or `TRUNC=BIN` inside `EZPARAMS`:
```text
TRUNC=BIN
ARITH=EXTEND
ROUND=YES
ADJUST-RECORD-LEN=YES
```
- `TRUNC=BIN` ensures binary integer fields conform to full machine word boundaries rather than decimal picture limits.
- `ARITH=EXTEND` allows intermediate calculations up to 31 decimal digits, preventing rounding drift.

### 2. Inspect Generated COBOL Source for File Status Handling
Check the intermediate COBOL emitted by IMU in `&&COBSRCE`:
```cobol
       READ INFILE
           AT END MOVE 'Y' TO WS-INFILE-EOF
       END-READ.
       IF WS-INFILE-STATUS NOT = '00' AND NOT = '10'
           MOVE WS-INFILE-STATUS TO WS-ERR-CODE
           PERFORM 9999-IO-ERROR
       END-IF.
```
If legacy Easytrieve code used relaxed file verification, configure `IO-ERROR=IGNORE` in IMU configuration.""",
        "prevention": [
            "Always compile IMU-generated COBOL with `TRUNC(BIN)` when dealing with binary integers (`USAGE BINARY` or `COMP`).",
            "Use SuperC with `LONGLN` option to compare numeric columns across 100,000+ output records.",
            "Verify packed-decimal signs by ensuring `NUMPROC(NOPFD)` is active if legacy data contains mixed signs."
        ],
        "references": [
            {"title": "IBM Migration Utility: Customizing EZPARAMS", "url": "https://www.ibm.com/docs/en/imu/5.1.0?topic=customizing-ezparams"},
            {"title": "IBM Enterprise COBOL for z/OS Arithmetic Differences", "url": "https://www.ibm.com/docs/en/cobol-zos/latest?topic=arithmetic-intermediate-results"}
        ]
    },
    {
        "slug": "ezt-report-layout-pagination-imu-tuning",
        "title": "Fixing Line Overflow, Heading Wraps, and Dynamic Page Breaks in IMU-Generated COBOL Reports",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Easytrieve", "IMU", "Reporting", "Pagination", "COBOL", "BMS"],
        "reading_time": "9 min read",
        "tldr": "Easytrieve's proprietary REPORT facility automatically calculates dynamic column spacing, header wrapping, and control breaks. Discover how IMU's FSCRPT00 module maps reporting macros to standard COBOL LINAGE clauses and page counters.",
        "problem": """A complex 132-column general ledger report converted from Easytrieve via IMU truncates summary footers, wraps account titles across two rows improperly, and fails to emit page break form-feed characters at exactly line 60, disrupting automated PDF archive indexing downstream.""",
        "root_cause": """Easytrieve contains a sophisticated dynamic reporting engine that handles:
- Automatic column positioning based on field widths and title lengths.
- Multi-level control breaks (`BEFORE-BREAK`, `AFTER-BREAK`, `TALLY`).
- Built-in pagination and title suppression on overflow.

When IMU translates an Easytrieve `REPORT` statement, it can generate either:
1. **Native COBOL Report Logic**: Emitting explicit `WRITE AFTER ADVANCING` statements and line counters.
2. **IMU Runtime Report Driver (`FSCRPT00`)**: Utilizing an optimized runtime table to ensure exact column alignment.""",
        "solution": """### 1. Configure IMU Report Emulation Parameters
In the job stream or global `EZPARAMS`, specify:
```text
REPORTE=NATIVE
AUTOSPACE=YES
LINESIZE=132
PAGESIZE=060
PAGE-HEADER=TOP
TOTALS=BOTTOM
```

### 2. Examine the Emitted COBOL LINAGE Clause
Inspect the emitted File Description entry:
```cobol
       FD  REPORT-FILE
           RECORDING MODE IS F
           LABEL RECORDS ARE STANDARD
           LINAGE IS 60 LINES
             WITH FOOTING AT 56
             LINES AT TOP 2
             LINES AT BOTTOM 2.
```

### 3. Verify Control Break Accumulators
Ensure `TALLY` and summary accumulators match the exact Easytrieve reset triggers:
```cobol
       IF WS-ACCT-BRANCH NOT = WS-PREV-BRANCH
           PERFORM 3000-PRINT-BRANCH-TOTALS
           MOVE 0 TO WS-BRANCH-ACCUMULATOR
           MOVE WS-ACCT-BRANCH TO WS-PREV-BRANCH
       END-IF.
```""",
        "prevention": [
            "Review reports with wide record layouts (e.g. 132 or 160 columns) to prevent printer wrap.",
            "Verify ANSI carriage control characters in column 1 (`' '`, `'0'`, `'-'`, `'1'`) using hex browse.",
            "Validate that `PAGE` number reset logic triggers accurately on top-level control breaks."
        ],
        "references": [
            {"title": "IBM Migration Utility: Easytrieve Report Facility Emulation", "url": "https://www.ibm.com/docs/en/imu/5.1.0?topic=reports-report-facility"},
            {"title": "StackMF Mainframe Modernization Practice", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },
    {
        "slug": "ezt-macro-substitution-imu-native-migration",
        "title": "Deconstructing Complex Easytrieve Macros and Tables into Standard COBOL Copybooks via IMU",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Easytrieve", "Macros", "IMU", "COBOL Copybooks", "Modernisation"],
        "reading_time": "10 min read",
        "tldr": "Legacy Easytrieve applications frequently rely on parameter-substituted %MACRO calls and internal memory tables. Learn how to map Easytrieve macro libraries to standard COBOL copybooks and replace binary SEARCH tables with clean OCCURS structures.",
        "problem": """An enterprise conversion initiative is blocked because hundreds of Easytrieve programs invoke proprietary macros (`%CALCTAX &RATE &BASE`) stored in a centralized PDS macro library (`PROD.EZT.MACLIB`). IMU throws error `FSCM012E UNRESOLVED MACRO REFERENCE` during the pre-compilation phase.""",
        "root_cause": """Easytrieve macros support dynamic positional and keyword argument substitution that behaves like an assembler preprocessor.
If IMU's `SYSLIB` concatenation cannot resolve the macro library or if the macro uses non-standard nested conditionals (`%IF ... %ELSE`), the translator fails to expand the code into compliant COBOL.""",
        "solution": """### 1. Add Macro Concatenation to IMU Translation JCL
Add the proprietary macro library to the `SYSLIB` DD of the `FSCCL1` step:
```jcl
//STEP1    EXEC PGM=FSCCL1
//STEPLIB  DD DSN=SYS1.IMU.SFSCLLMD,DISP=SHR
//SYSLIB   DD DSN=PROD.EZT.MACLIB,DISP=SHR
//         DD DSN=PROD.COBOL.COPYLIB,DISP=SHR
//SYSIN    DD DSN=PROD.EZT.SRCLIB(PGM01),DISP=SHR
```

### 2. Refactor Easytrieve Internal Tables into COBOL SEARCH
Convert Easytrieve table lookups:
```ezt
* Legacy Easytrieve Table
TABLE STATE-TBL 'AL' 'ALABAMA' 'AK' 'ALASKA' 'AZ' 'ARIZONA'
LOOKUP STATE-NAME = STATE-TBL (STATE-CODE)
```
Into standard Enterprise COBOL:
```cobol
       01  STATE-TABLE-DATA.
           05  FILLER PIC X(17) VALUE 'ALALABAMA        '.
           05  FILLER PIC X(17) VALUE 'AKALASKA         '.
           05  FILLER PIC X(17) VALUE 'AZARIZONA        '.
       01  STATE-TABLE REDEFINES STATE-TABLE-DATA.
           05  STATE-ENTRY OCCURS 3 TIMES
                           ASCENDING KEY IS ST-CODE
                           INDEXED BY ST-IDX.
               10  ST-CODE       PIC X(02).
               10  ST-NAME       PIC X(15).

       PROCEDURE DIVISION.
           SEARCH ALL STATE-ENTRY
               AT END MOVE 'UNKNOWN' TO WS-STATE-NAME
               WHEN ST-CODE (ST-IDX) = WS-INPUT-STATE
                   MOVE ST-NAME (ST-IDX) TO WS-STATE-NAME
           END-SEARCH.
```""",
        "prevention": [
            "Audit all members in `PROD.EZT.MACLIB` prior to migration to identify obsolete macro dependencies.",
            "De-duplicate redundant macro definitions by establishing standardized enterprise COBOL copybooks.",
            "Test multi-level table lookups with boundary test cases to ensure search index parity."
        ],
        "references": [
            {"title": "IBM Migration Utility: Handling Easytrieve Macros", "url": "https://www.ibm.com/docs/en/imu/5.1.0?topic=macros-migration-utility"},
            {"title": "StackMF Enterprise Full-Stack Mainframe Pods", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },
    {
        "slug": "vscode-zowe-explorer-setup-enterprise-sso",
        "title": "Configuring VS Code Zowe Explorer with Enterprise SSO, Team Profiles, and API Mediation Layer (APIML)",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["Zowe", "VS Code", "Zowe Explorer", "APIML", "SSO", "DevOps"],
        "reading_time": "11 min read",
        "tldr": "Elevate mainframe developer productivity by moving from 3270 green-screens to Visual Studio Code. Discover how to configure Zowe Explorer v2 with team configuration profiles (`zowe.config.json`), secure client certificates, and Single Sign-On (SSO) via the Zowe API Mediation Layer.",
        "problem": """Enterprise mainframe developers install the Zowe Explorer extension in VS Code but encounter constant credential prompts, connection timeouts, or SSL handshake failures when connecting to z/OSMF:
```text
Zowe Explorer: Error connecting to session 'zsys1'.
Request failed with status code 401: Unauthorized.
JWT Token expired or APIML routing unavailable.
```
Developers revert to 3270 emulators because team profile configurations are not standardized across workstations.""",
        "root_cause": """Zowe Explorer v2 introduced team configuration files (`zowe.config.json`):
- Instead of individual engineers storing plaintext credentials in local user profiles, enterprise organizations centralize mainframe gateway endpoints, API Mediation Layer (APIML) URLs, and certificate authorities.
- If the APIML gateway certificate is not trusted by Node.js/VS Code or if JWT token expiration is misconfigured, authentication fails.""",
        "solution": """### 1. Initialize an Enterprise Team Configuration
In the root of your developer workspace or home directory, create `zowe.config.json`:
```json
{
  "$schema": "https://zowe.org/schemas/zowe.config.json",
  "profiles": {
    "base": {
      "type": "base",
      "properties": {
        "host": "apiml.mainframe.stackmf.internal",
        "port": 7554,
        "rejectUnauthorized": false
      },
      "secure": []
    },
    "apiml": {
      "type": "apiml",
      "properties": {
        "authType": "token"
      }
    },
    "zosmf": {
      "type": "zosmf",
      "properties": {
        "port": 443,
        "basePath": "/api/v1"
      }
    }
  },
  "defaults": {
    "base": "base",
    "zosmf": "zosmf"
  }
}
```

### 2. Authenticate Using Enterprise SSO / Login Command
Open the VS Code integrated terminal and authenticate to generate an encrypted JSON Web Token (JWT):
```bash
zowe auth login apiml
```
Enter your enterprise RACF / ACF2 / Top Secret credentials. Zowe securely saves the token in your operating system credential vault (Windows Credential Manager / macOS Keychain).

### 3. Access Datasets, USS Files, and JES Spool in VS Code
Open the Zowe Explorer viewlet:
- Under **Data Sets**, click `+` and enter pattern `PROD.COBOL.*`.
- Browse, edit, syntax-highlight, and save datasets with instant automatic z/OS synchronization!
- Under **Jobs**, submit JCL and inspect spool output without ever opening TSO/ISPF!""",
        "prevention": [
            "Store `zowe.config.json` templates in corporate Git repositories for one-click developer onboarding.",
            "Use Zowe API Mediation Layer (APIML) to route all z/OS services through a single port with SSO.",
            "Never store plaintext mainframe passwords in `.env` or config files; enforce OS credential vaults."
        ],
        "references": [
            {"title": "Open Mainframe Project: Zowe Explorer Documentation", "url": "https://docs.zowe.org/stable/user-guide/ze-usage"},
            {"title": "VS Code Marketplace: Zowe Explorer Extension", "url": "https://marketplace.visualstudio.com/items?itemName=Zowe.vscode-extension-for-zowe"},
            {"title": "StackMF Mainframe Modernization Hub", "url": "https://stackmf.com/#fullstack-bridge"}
        ]
    },
    {
        "slug": "zowe-cli-batch-jcl-submission-automation",
        "title": "Automating z/OS JCL Submission, Spool Polling, and Output Retrieval via Zowe CLI in CI/CD",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["Zowe CLI", "JCL", "CI/CD", "GitHub Actions", "Spool Parsing", "Automation"],
        "reading_time": "10 min read",
        "tldr": "Integrate mainframe batch execution into modern DevOps pipelines. Learn how to submit JCL from local Git branches, wait for completion, check return codes, and download spool outputs (SYSUDUMP, CEEDUMP) programmatically using Zowe CLI commands.",
        "problem": """DevOps teams attempting to automate regression testing in GitHub Actions or Jenkins struggle to trigger mainframe batch jobs. Engineers resort to manual submission or flaky FTP scripts that fail to report whether the submitted batch job succeeded, timed out, or crashed with an ABEND.""",
        "root_cause": """Submitting batch jobs across network boundaries requires interacting with the z/OSMF Jobs REST API.
Zowe CLI abstracts these complex HTTP calls into simple command-line invocations:
- `zowe zos-jobs submit` handles dataset or local file submission.
- The `--wait-for-active` and `--wait-for-output` flags pause execution until the job completes in JES2/JES3.
- Return codes (`CC 0000`, `ABEND S0C7`) are captured natively as shell exit codes.""",
        "solution": """### 1. Submit Local JCL and Wait for Completion
In your CI/CD runner or terminal:
```bash
zowe zos-jobs submit local-file ./jcl/TESTPAY01.jcl \
     --wait-for-output \
     --view-all-spool-content
```
Output returns:
```text
jobid:   JOB04821
jobname: TESTPAY01
status:  OUTPUT
retcode: CC 0000
```

### 2. Evaluate Return Code Programmatically in Bash Script
Create an automated test verification script:
```bash
#!/usr/bin/env bash
set -e

echo "Submitting batch job..."
RESPONSE=$(zowe zos-jobs submit local-file ./jcl/TESTPAY01.jcl --wait-for-output --response-format-json)

JOB_ID=$(echo "$RESPONSE" | jq -r '.data.jobid')
RET_CODE=$(echo "$RESPONSE" | jq -r '.data.retcode')

echo "Job $JOB_ID completed with: $RET_CODE"

if [[ "$RET_CODE" != "CC 0000" && "$RET_CODE" != "CC 0004" ]]; then
  echo "ERROR: Batch test failed! Downloading CEEDUMP..."
  zowe zos-jobs download spool-file-by-id "$JOB_ID" 4 --file "./logs/CEEDUMP.txt"
  exit 1
fi

echo "Batch verification passed successfully!"
```

### 3. Download Specific Spool Datasets
Download only SYSPRINT to verify application outputs:
```bash
zowe zos-jobs view spool-file-by-id JOB04821 3 > ./logs/SYSPRINT.txt
```""",
        "prevention": [
            "Always specify `--wait-for-output` in automated pipelines to prevent race conditions.",
            "Extract job metadata via `--response-format-json` and parse with `jq` for robust error handling.",
            "Archive spool outputs as build artifacts in GitHub Actions / GitLab for post-mortem analysis."
        ],
        "references": [
            {"title": "Open Mainframe Project: Zowe CLI zos-jobs Command Group", "url": "https://docs.zowe.org/stable/web_help/index.html?cmd=zowe_zos-jobs"},
            {"title": "StackMF Broadcom Replacement & DevOps Services", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },
    {
        "slug": "zowe-cli-vsam-dataset-management-scripts",
        "title": "Scripting VSAM and Partitioned Dataset (PDS/PDSE) Operations using Zowe CLI and Python",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["Zowe CLI", "VSAM", "Python", "Datasets", "PDS", "Automation"],
        "reading_time": "10 min read",
        "tldr": "Manage z/OS datasets like cloud storage. Discover how to create, upload, download, and delete PDS members and VSAM clusters programmatically using the Zowe CLI and Python subprocess workflows.",
        "problem": """Test data provisioning on the mainframe is notoriously slow and manual. Developers wait days for database administrators to run IDCAMS REPROs or allocation jobs just to populate a test VSAM cluster or update copybooks in a shared test library.""",
        "root_cause": """Direct interaction with z/OS datasets historically required TSO/ISPF 3.2 panels or IDCAMS batch jobs.
Using Zowe CLI's `zos-files` module, developers can provision datasets on-demand via scripts running on their laptops or CI/CD runners.""",
        "solution": """### 1. Allocate a New PDSE for COBOL Source
```bash
zowe zos-files create data-set-partitioned "DEV.USER.COBOL" \
     --block-size 27920 \
     --record-format FB \
     --record-length 80 \
     --directory-blocks 20 \
     --size 5CYL \
     --type LIBRARY
```

### 2. Upload Local Source Files to Mainframe Members
```bash
zowe zos-files upload file-to-data-set "./src/ACCNTREC.cbl" "DEV.USER.COBOL(ACCNTREC)"
```

### 3. Provision VSAM Test Clusters via Python
Automate IDCAMS cluster allocation using Python:
```python
import subprocess
import json

idcams_script = '''
  DEFINE CLUSTER (NAME('DEV.TEST.CUSTOMER.KSDS') -
         CYLINDERS(2 1) -
         RECORDSIZE(250 250) -
         KEYS(10 0) -
         SHAREOPTIONS(2 3)) -
         DATA (NAME('DEV.TEST.CUSTOMER.KSDS.DATA')) -
         INDEX (NAME('DEV.TEST.CUSTOMER.KSDS.INDEX'))
'''

cmd = [
    "zowe", "zos-console", "issue", "command",
    f"EX 'SYS1.PROCLIB(IDCAMS)'",
    "--response-format-json"
]

print("Executing automated VSAM provisioning...")
subprocess.run(["zowe", "zos-files", "upload", "stdin-to-data-set", "DEV.IDCAMS.SYSIN"], input=idcams_script.encode())
subprocess.run(["zowe", "zos-jobs", "submit", "data-set", "DEV.JCL.CNTL(RUNIDCAM)", "--wait-for-output"])
print("VSAM cluster provisioned successfully!")
```""",
        "prevention": [
            "Use `--type LIBRARY` (PDSE) instead of classic PDS to avoid directory block exhaustion.",
            "Automate teardown of temporary test datasets after CI/CD test suite completion.",
            "Verify that dataset high-level qualifiers (HLQs) conform to RACF dataset profile conventions."
        ],
        "references": [
            {"title": "Open Mainframe Project: Zowe CLI zos-files Commands", "url": "https://docs.zowe.org/stable/web_help/index.html?cmd=zowe_zos-files"},
            {"title": "StackMF Dedicated Mainframe Engineering Pods", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },
    {
        "slug": "vscode-zowe-cobol-language-server-lsp",
        "title": "Enabling Advanced COBOL Syntax Checking, Copybook Resolution, and Hover Peek in VS Code",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["VS Code", "COBOL", "LSP", "Language Server", "Copybooks", "Developer Productivity"],
        "reading_time": "9 min read",
        "tldr": "Transform Visual Studio Code into a full-featured COBOL IDE. Configure the COBOL Language Support extension (Language Server Protocol / LSP), local and remote copybook caching via Zowe, and real-time syntax linting before submitting jobs to z/OS.",
        "problem": """Developers editing COBOL code in basic text editors or green-screens don't see syntax errors until after submitting a compile job and waiting for compiler diagnostics. Furthermore, pressing F12 or hovering over `COPY` statements fails to resolve copybooks, forcing developers to open separate browse sessions.""",
        "root_cause": """Modern IDE capabilities (go-to-definition, hover documentation, syntax errors in red squiggles) rely on the Language Server Protocol (LSP).
Without proper copybook path mapping in VS Code settings, the COBOL LSP parser cannot resolve copybook files located on local disks or z/OS PDS libraries.""",
        "solution": """### 1. Install Essential Mainframe Extensions
In VS Code, install:
- `Zowe.vscode-extension-for-zowe` (Zowe Explorer)
- `che-incubator.cobol-language-support` (Broadcom / Open Mainframe COBOL Language Support)
- `IBM.ibm-zopeneditor` (IBM Z Open Editor)

### 2. Configure `.vscode/settings.json` for Copybook Resolution
Add the following configuration to your workspace:
```json
{
  "zopeneditor.cobol.copybookDirs": [
    "./copybooks",
    "../common-copybooks"
  ],
  "zopeneditor.zowe": {
    "defaultCliProfile": "zosmf"
  },
  "zopeneditor.cobol.remoteCopybookPredefinedDirs": [
    "PROD.COBOL.COPYLIB",
    "DEV.COMMON.COPYLIB"
  ],
  "cobol.compiler_options": "OPT(2),ARCH(14),NUMPROC(PFD)"
}
```

### 3. Real-Time Developer Features
- **Hover Peek**: Hover your cursor over `WS-CUSTOMER-RECORD` to instantly see its 01-level hierarchy and PIC definitions.
- **Go to Definition (`F12`)**: Press F12 on `COPY INVOICE` to immediately open and view `INVOICE.cpy` in a split editor.
- **Inline Linting**: Syntax errors (e.g. typing `PERFROM` instead of `PERFORM`) are underlined in red immediately as you type!""",
        "prevention": [
            "Check `.vscode/settings.json` into your Git repository so all team members inherit the same copybook paths.",
            "Leverage IBM Z Open Editor's auto-format to maintain standard 80-column margin alignment (Columns 8-72 for code).",
            "Enable pre-commit hooks that run the LSP linter to catch errors before code is pushed to GitHub."
        ],
        "references": [
            {"title": "IBM Z Open Editor Documentation", "url": "https://www.ibm.com/docs/en/developer-for-zos/latest?topic=editor-z-open"},
            {"title": "Open Mainframe Project: COBOL Language Support", "url": "https://github.com/eclipse-che4z/che-che4z-lsp-for-cobol"}
        ]
    },
    {
        "slug": "zowe-api-mediation-layer-onboarding-services",
        "title": "Onboarding Custom Mainframe REST Services to Zowe API Mediation Layer (APIML) with Eureka Discovery",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Zowe", "APIML", "REST API", "Eureka", "API Gateway", "Modernisation"],
        "reading_time": "11 min read",
        "tldr": "The Zowe API Mediation Layer (APIML) provides a central enterprise gateway, SSO, and service discovery for all mainframe REST APIs. Learn how to onboard custom z/OS Connect or Java Spring Boot services using Netflix Eureka registration and Swagger/OpenAPI schemas.",
        "problem": """Enterprises building dozens of microservices on z/OS find their cloud developers overwhelmed by fragmented mainframe endpoints, multiple port numbers, varying authentication methods, and lack of dynamic failover.""",
        "root_cause": """Individual mainframe subsystems (z/OSMF, z/OS Connect, CICS, IMS Mobile) run on disparate TCP ports with differing security schemes.
The **Zowe API Mediation Layer (APIML)** implements an enterprise API Gateway based on Spring Cloud Gateway and Netflix Eureka:
- Provides a single secure entry point (`https://mainframe-gateway:7554/api/v1/...`).
- Validates enterprise tokens (JWT / RACF passTickets) once at the perimeter.
- Auto-discovers active backend service instances dynamically.""",
        "solution": """### 1. Create the Service Onboarding Configuration (`api-defs.yml`)
Define your service metadata:
```yaml
serviceId: banking-core-service
title: Enterprise Core Banking REST API
description: Real-time accounts, ledger posting, and card transactions via CICS & DB2
instance:
  homePageUrl: https://zsys1.stackmf.internal:10443/
  statusPageUrl: https://zsys1.stackmf.internal:10443/status
  healthCheckUrl: https://zsys1.stackmf.internal:10443/healthz
routedServices:
  - gatewayUrl: api/v1/banking
    serviceUrl: /api/v1
routes:
  - gatewayUrl: api/v1/banking
    serviceUrl: /api/v1
apiInfo:
  - version: 1.0.0
    swaggerUrl: https://zsys1.stackmf.internal:10443/swagger/v3/api-docs
authentication:
  scheme: httpBasicPassTicket
  applid: CICSPROD
```

### 2. Register Service with the Zowe Discovery Service
Post the registration payload to APIML Discovery Service:
```bash
curl -X POST https://apiml.stackmf.internal:7553/eureka/apps/BANKING-CORE-SERVICE \
     -H "Content-Type: application/json" \
     -d @api-defs.json
```

### 3. Invoke Service via Unified APIML Gateway
Cloud clients now invoke the API via standard HTTPS:
```bash
curl -X GET https://apiml.stackmf.internal:7554/banking-core-service/api/v1/accounts/49201 \
     -H "Authorization: Bearer <ZOWE_JWT_TOKEN>"
```""",
        "prevention": [
            "Always register health check endpoints (`/healthz`) so APIML routes around degraded LPARs automatically.",
            "Use PassTickets to authenticate seamlessly to backend CICS/IMS regions without exposing user passwords.",
            "Publish OpenAPI 3.0 specifications to the Zowe API Catalog for developer self-service documentation."
        ],
        "references": [
            {"title": "Open Mainframe Project: Zowe API Mediation Layer Overview", "url": "https://docs.zowe.org/stable/user-guide/api-mediation-layer"},
            {"title": "StackMF Modernization Architecture", "url": "https://stackmf.com/#fullstack-bridge"}
        ]
    },
    {
        "slug": "zowe-cross-memory-server-zowe-aux-troubleshooting",
        "title": "Diagnosing Zowe Cross-Memory Server (ZWESVSRV) and Aux Server Security Exceptions",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["Zowe", "Cross-Memory Server", "ZWESVSRV", "APF", "RACF", "Troubleshooting"],
        "reading_time": "10 min read",
        "tldr": "The Zowe Cross-Memory Server (ZWESVSRV) provides privileged z/OS services to unprivileged user tasks. Troubleshoot common startup abends (S0C4, S047) caused by missing APF authorization, PPT entries, and RACF FACILITY class permissions.",
        "problem": """During z/OS IPL or Zowe startup, the Cross-Memory Server STC fails to initialize:
```text
ZWES0101E ZWESVSRV INITIALIZATION FAILED. RETURN CODE = 16 REASON = 00000028
CSV019I LOAD FAILED FOR MODULE ZWESAUX, RETURN CODE = 04
IEF450I ZWESVSRV ZWESVSRV - ABEND=S047 U0000 REASON=00000000
```
Without the Cross-Memory Server active, Zowe Desktop and Zowe CLI secure data operations fail.""",
        "root_cause": """ZWESVSRV requires authorized supervisor-state execution to switch address spaces and inspect memory:
- **ABEND S047**: An unauthorized program issued a supervisor call or privileged instruction. Occurs when the Zowe load library (`SZWEAUTH`) is not APF-authorized.
- **Reason 00000028**: Missing RACF security profile permissions in the `FACILITY` class (`ZWES.IS`).
- **Missing SCHEDxx Entry**: The Program Properties Table (PPT) entry defining the STC as non-swappable and privileged is missing.""",
        "solution": """### 1. Add APF Authorization for Zowe Load Libraries
In the active MVS console or `SYS1.PARMLIB(PROGxx)`:
```text
SETPROG APF,ADD,DSNAME=SYS1.ZOWE.SZWEAUTH,VOLUME=VOL001
```

### 2. Verify Program Properties Table (SCHEDxx)
Ensure `SYS1.PARMLIB(SCHEDxx)` contains:
```text
PPT PGMNAME(ZWESVSRV)
    NOSWAP
    PRIV
    SYST
```
Activate dynamically:
```text
SET SCH=(01)
```

### 3. Grant Required RACF FACILITY Permissions
Ensure the Zowe started task user has access:
```text
RDEFINE FACILITY ZWES.IS UACC(NONE)
PERMIT ZWES.IS CLASS(FACILITY) ID(ZWESVUSR) ACCESS(READ)
SETROPTS RACLIST(FACILITY) REFRESH
```

### 4. Restart the Started Task
```text
/S ZWESVSRV
```
Verify the log confirms: `ZWES0100I ZWESVSRV INITIALIZATION COMPLETED SUCCESSFULLY`.""",
        "prevention": [
            "Audit APF authorization lists after every z/OS maintenance apply (`SMP/E APPLY`).",
            "Ensure the dataset containing `ZWESAUX` resides on a secure, SMS-managed system volume.",
            "Verify that Zowe started task user IDs are defined with `PROTECTED` attribute in RACF."
        ],
        "references": [
            {"title": "Open Mainframe Project: Configuring Zowe Cross-Memory Server", "url": "https://docs.zowe.org/stable/user-guide/configure-xmem-server"},
            {"title": "IBM z/OS MVS Initialization and Tuning Reference: SCHEDxx", "url": "https://www.ibm.com/docs/en/zos/latest?topic=definitions-schedxx"}
        ]
    },
    {
        "slug": "ibm-developer-for-zos-idz-remote-debugging",
        "title": "Setting up Remote COBOL/PL/I Debug Sessions in IBM Developer for z/OS (IDz) using Debug Tool",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["IDz", "COBOL", "Remote Debug", "Debug Tool", "Eclipse", "z/OS Debugger"],
        "reading_time": "11 min read",
        "tldr": "Step-by-step guide to configuring interactive source-level debugging for batch and CICS COBOL applications inside IBM Developer for z/OS (IDz). Discover how to configure TEST compiler options, establish TCP/IP daemon connections, and trigger breakpoints dynamically.",
        "problem": """Developers spend days inserting temporary `DISPLAY` statements into 5,000-line COBOL programs to trace elusive logic bugs. Re-compiling and promoting code just to inspect variables burns immense CPU and delays incident turnaround.""",
        "root_cause": """IBM Developer for z/OS (IDz) pairs with the **IBM z/OS Debugger** backend.
When properly configured:
- The mainframe program executes under control of Language Environment's `TEST` runtime parameter.
- It opens a reverse TCP/IP connection to the developer's workstation running the IDz Debug Daemon (typically on port 8001).
- The developer steps through live COBOL code, sets breakpoints, and inspects variables in real-time within the IDz GUI.""",
        "solution": """### 1. Compile COBOL with the TEST Option
Ensure the compile step generates DWARF debugging information:
```jcl
//COBSTEP EXEC PGM=IGYCRCTL,
//  PARM='TEST(SOURCE,SEPARATE),OPT(0),ARCH(14)'
//SYSDEBUG DD DSN=DEV.USER.SYSDEBUG(ACCNTREC),DISP=SHR
```
Using `TEST(SEPARATE)` stores debug tables in a separate side-file (`SYSDEBUG`), keeping production load module sizes minimal.

### 2. Start the IDz Debug Daemon on Your Workstation
In IDz:
1. Open the **Debug** perspective.
2. Ensure the daemon icon in the toolbar indicates **Debug Daemon Listening on port 8001**.
3. Note your workstation IP address (e.g., `10.14.20.105`).

### 3. Pass TEST Runtime Options in Batch JCL
Add the `CEEOPTS` DD statement to your execution JCL:
```jcl
//RUNSTEP  EXEC PGM=ACCNTREC
//STEPLIB  DD DSN=DEV.USER.LOADLIB,DISP=SHR
//         DD DSN=EQAW.SEQAMOD,DISP=SHR
//CEEOPTS  DD *
  TEST(ALL,*,PROMPT,TCPIP&10.14.20.105%8001:)
/*
```

### 4. Interactive Debugging in IDz
Upon launching the batch job, execution immediately suspends at statement 1:
- IDz opens the COBOL source automatically.
- Press **F5** to step into, **F6** to step over.
- Hover over any variable to inspect or modify its value in memory!""",
        "prevention": [
            "Use `TEST(NOHOOK,SEPARATE)` for production modules to enable on-demand diagnostics without performance penalties.",
            "Verify local firewall rules permit inbound TCP traffic on port 8001 from the z/OS LPAR IP range.",
            "Store `.dbg` / `SYSDEBUG` side-files in centralized test libraries with automated lifecycle retention."
        ],
        "references": [
            {"title": "IBM Developer for z/OS: Debugging Applications", "url": "https://www.ibm.com/docs/en/developer-for-zos/latest?topic=debugging-applications"},
            {"title": "IBM z/OS Debugger User's Guide (SC27-9257)", "url": "https://www.ibm.com/docs/en/debug-for-zos/latest"},
            {"title": "StackMF Mainframe Engineering Pods", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },
    {
        "slug": "idz-workspace-project-synchronization-git",
        "title": "Integrating IDz with Git and IBM Dependency Based Build (DBB) for Branch-Based Development",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["IDz", "Git", "IBM DBB", "DevOps", "Branching", "Modernisation"],
        "reading_time": "10 min read",
        "tldr": "Connect IBM Developer for z/OS (IDz) with Git repositories and IBM DBB. Learn how to map z/OS projects to local Git clones, manage branch checkouts, and trigger automated User Builds on z/OS directly from the IDz interface.",
        "problem": """Mainframe teams adopting Git struggle because traditional mainframe tools assume code lives in PDS libraries. Developers manually copy files between Git folders and mainframe datasets, leading to version drift and build failures.""",
        "root_cause": """IDz includes native EGit integration. When paired with **IBM Dependency Based Build (DBB)**:
- Code is cloned locally into an IDz z/OS Project.
- Developers create Git feature branches (`feature/billing-update`).
- Right-clicking any COBOL file and choosing **User Build** invokes a DBB Groovy script on z/OS that compiles the code in private development datasets without polluting production.""",
        "solution": """### 1. Clone Git Repository into IDz
In IDz:
1. Open **Git Repositories** view &rarr; **Clone a Git repository**.
2. Enter repository URL: `git@github.com:stackmf/mainframe-core.git`.
3. Import as a **z/OS Project**.

### 2. Configure DBB User Build Properties
Create `build.properties` in your repository root:
```properties
# DBB Build Configuration
workDir=/u/users/anshu/workspace
dbb.home=/usr/lpp/IBM/dbb
hlq=DEV.USER
cobol.compiler=IGYCRCTL
cobol.compileOptions=OPT(2),ARCH(14),NUMPROC(PFD)
```

### 3. Trigger User Build
1. In the IDz Project Explorer, right-click `ACCNTREC.cbl`.
2. Select **User Build**.
3. IDz automatically transfers the modified source and required copybooks to z/OS USS, executes the DBB Groovy build script, and parses compiler error markers directly into the IDz Problems view!""",
        "prevention": [
            "Enforce `.gitattributes` to ensure COBOL and copybooks maintain correct EBCDIC (`IBM-1047`) and UTF-8 mapping.",
            "Establish automated branch protection on `main` to mandate pull request approvals.",
            "Use DBB Metastore to track impact analysis so builds recompile only affected modules."
        ],
        "references": [
            {"title": "IBM Dependency Based Build Documentation", "url": "https://www.ibm.com/docs/en/dbb/latest"},
            {"title": "StackMF Git-Native Mainframe Engineering", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },
    {
        "slug": "idz-code-review-ruleset-customization",
        "title": "Customizing Software Analyzer and Code Quality Rulesets in IDz for Enterprise COBOL Standards",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["IDz", "Code Quality", "Software Analyzer", "COBOL", "Standards", "Linter"],
        "reading_time": "9 min read",
        "tldr": "Enforce strict coding standards across your mainframe team. Configure IBM Developer for z/OS (IDz) Software Analyzer rulesets to automatically flag dangerous patterns like GOTO, hardcoded SQL credentials, and uninitialized packed decimals.",
        "problem": """Legacy codebases accumulate technical debt, unhandled errors, and non-performant constructs (`PERFORM ... THROUGH`, un-indexed table searches). Code reviews are manual and inconsistent, allowing buggy patterns to slip into production.""",
        "root_cause": """IDz includes the **Software Analyzer** engine, capable of static AST (Abstract Syntax Tree) analysis across COBOL, PL/I, and SQL.
By defining custom rulesets, organizations establish automated gates that warn or fail builds when code violates security or performance standards.""",
        "solution": """### 1. Create a Custom Enterprise Ruleset (`ruleset.xml`)
In IDz:
1. Navigate to **Window &rarr; Preferences &rarr; Software Analyzer &rarr; Rules and Categories**.
2. Select **COBOL** and create ruleset `Enterprise-COBOL-Standard`:
   - Flag all `ALTER` statements (Severe).
   - Flag `GOTO` statements jumping outside current paragraph (Error).
   - Require `FILE STATUS` check immediately following any `READ` or `WRITE` (Warning).
   - Flag unconstrained `OCCURS DEPENDING ON` (Warning).

### 2. Run Static Analysis in IDz
Right-click your source folder &rarr; **Software Analysis &rarr; Run As &rarr; Enterprise-COBOL-Standard**.
The **Software Analyzer Results** view displays all violations with direct navigation to the offending source line.

### 3. Export Ruleset for Headless CI/CD Scanning
Export rules to XML and run headless in your pipeline:
```bash
/usr/lpp/IBM/idz/bin/code-review.sh \
  -ruleFile ./config/ruleset.xml \
  -sourceDir ./src \
  -outputDir ./reports/code-review-report.html
```""",
        "prevention": [
            "Integrate IDz Code Review into automated pull request checks in GitHub Actions.",
            "Block PR merging if severe ruleset violations exist.",
            "Update rulesets periodically to reflect modern Enterprise COBOL 6.x performance best practices."
        ],
        "references": [
            {"title": "IBM Developer for z/OS: Performing Code Review", "url": "https://www.ibm.com/docs/en/developer-for-zos/latest?topic=analyzing-code-review"},
            {"title": "StackMF Mainframe Application Maintenance (AMS)", "url": "https://stackmf.com/#maintenance-ams"}
        ]
    },
    {
        "slug": "zowe-explorer-ftp-vs-zftp-performance-tuning",
        "title": "Eliminating Latency in VS Code Zowe Explorer: Tuning z/OS FTP Server and USS Buffers",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["Zowe Explorer", "FTP", "z/OSMF", "Performance", "VS Code", "Latency"],
        "reading_time": "9 min read",
        "tldr": "When browsing thousands of PDS members in Zowe Explorer, high network latency and unoptimized z/OS FTP/z/OSMF buffer settings can cause sluggish rendering. Learn how to tune z/OSMF heap sizes, enable client caching, and switch to high-speed z/OS FTP protocol profiles.",
        "problem": """Developers opening large partitioned datasets (`SYS1.MACLIB` or multi-thousand member source libraries) in VS Code Zowe Explorer experience 10-20 second beachballs before member lists load, degrading developer adoption.""",
        "root_cause": """By default, Zowe Explorer uses the z/OSMF REST API over HTTPS:
- z/OSMF processes JSON responses containing metadata for each individual member.
- For a PDS with 10,000 members, serialized JSON generation inside WebSphere Liberty Profile on z/OS causes CPU spikes and high network packet overhead.
- In high-latency WAN connections, switching to the lightweight `zftp` plugin or increasing z/OSMF Liberty heap dramatically accelerates response times.""",
        "solution": """### 1. Install and Configure the Zowe zFTP Plugin
The `zftp` plugin utilizes native z/OS FTP server with direct binary streaming:
```bash
zowe plugins install @zowe/zos-ftp-for-zowe-cli
```
In `zowe.config.json`, configure the `zftp` profile:
```json
{
  "profiles": {
    "myftp": {
      "type": "zftp",
      "properties": {
        "host": "zsys1.stackmf.internal",
        "port": 21,
        "user": "DEVUSER"
      }
    }
  }
}
```

### 2. Enable Client-Side Member Caching in VS Code
In `.vscode/settings.json`:
```json
{
  "zowe.explorer.maxItemsPerPage": 200,
  "zowe.explorer.enableCaching": true,
  "zowe.explorer.cachingDurationMinutes": 60
}
```

### 3. Tune z/OSMF JVM Heap Settings
In `SYS1.PARMLIB(IZUPRMxx)` or `jvm.options`:
```text
-Xms512m
-Xmx2048m
-XX:+UseG1GC
```""",
        "prevention": [
            "Use dataset filter masks (e.g. `PROD.COBOL(ACCT*)`) rather than fetching entire 10,000-member PDS catalogs.",
            "Enable G1 Garbage Collector in z/OSMF Liberty profile to avoid stop-the-world JVM pauses.",
            "Use PDSE datasets (`DSNTYPE=LIBRARY`) which provide faster directory reading than legacy PDS."
        ],
        "references": [
            {"title": "Open Mainframe Project: Zowe CLI zFTP Plugin", "url": "https://github.com/zowe/zftp-for-zowe-cli"},
            {"title": "IBM z/OSMF Configuration Guide: Performance Tuning", "url": "https://www.ibm.com/docs/en/zos/latest?topic=zosmf-tuning-performance"}
        ]
    },
    {
        "slug": "zowe-chat-mattermost-slack-ops-integration",
        "title": "Implementing Mainframe ChatOps with Zowe Chat: Managing Sysplex Incidents from Teams and Slack",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Zowe Chat", "ChatOps", "Slack", "Microsoft Teams", "Incident Response", "Automation"],
        "reading_time": "9 min read",
        "tldr": "Bring modern ChatOps to IBM z/OS. Discover how to configure Zowe Chat to inspect batch jobs, query MVS console messages, and recycle CICS transactions directly from Slack, Microsoft Teams, or Mattermost incident war rooms.",
        "problem": """During critical production bridge calls, incident managers must repeatedly ask mainframe system programmers to log into TSO, run SDSF, and read job return codes, slowing down Mean Time to Acknowledge (MTTA) and resolution.""",
        "root_cause": """Mainframe operational tools are isolated behind 3270 terminals.
**Zowe Chat** provides a secure, bidirectional ChatOps bridge:
- Listens to incident channels in Slack, Teams, or Mattermost.
- Authenticates users against enterprise LDAP and mainframe security (RACF).
- Executes validated, audited commands via z/OSMF and returns formatted card responses.""",
        "solution": """### 1. Deploy the Zowe Chat Server
Configure `zowe-chat.yaml`:
```yaml
chat:
  platform: slack
  botToken: "xoxb-your-slack-bot-token"
  appToken: "xapp-your-slack-app-token"
zowe:
  apiml:
    host: "apiml.stackmf.internal"
    port: 7554
security:
  rbac:
    adminUsers: ["anshu", "narendra"]
```

### 2. Issue Commands Directly from Slack / Teams
In your incident response channel:
```text
@zowe job status JOBPAY01
```
Zowe Chat replies within 1 second:
```text
Job: JOBPAY01 (JOB04921)
Status: ABENDED (S0C7)
Step: STEP020
System: LPAR1
Action: Click [View CEEDUMP] or [Restart Step]
```

### 3. Check System Health
```text
@zowe system status
```
Returns CPU utilization, peak 4HRA MIPS, active CICS regions, and critical WTO message alerts!""",
        "prevention": [
            "Enforce Role-Based Access Control (RBAC) in Zowe Chat to restrict update commands to authorized personnel.",
            "Audit all ChatOps commands in SMF Type 119 records for compliance logging.",
            "Integrate Zowe Chat alerts directly with PagerDuty and ServiceNow."
        ],
        "references": [
            {"title": "Open Mainframe Project: Zowe Chat User Guide", "url": "https://docs.zowe.org/stable/user-guide/zowe-chat-overview"},
            {"title": "StackMF 24/7 Managed Application Maintenance (AMS)", "url": "https://stackmf.com/#maintenance-ams"}
        ]
    },
    {
        "slug": "migrating-broadcom-file-master-to-zowe-data-sets",
        "title": "Replacing Broadcom File Master Plus with Zowe CLI and VS Code Hex Viewers",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["File Master Plus", "Broadcom Replacement", "Zowe", "VS Code", "Hex Viewer", "VSAM"],
        "reading_time": "10 min read",
        "tldr": "Eliminate hefty Broadcom File Master Plus licensing fees. Learn how to inspect, edit, and format raw sequential, PDS, and VSAM records using Zowe CLI, VS Code Hex Editor, and copybook record mapping scripts.",
        "problem": """Broadcom renewal quotes include exorbitant line-item charges for File Master Plus. Developers only use it to view VSAM records formatted with COBOL copybooks or edit hexadecimal packed-decimal values, making the software cost unjustifiable.""",
        "root_cause": """File Master Plus provides a 3270 formatted browser for records overlaid with COBOL copybook layouts.
Modern open-source alternatives achieve the exact same capability at zero license cost:
- **Zowe Explorer** downloads and streams datasets directly.
- **VS Code Hex Editor** (`ms-vscode.hexeditor`) inspects and modifies binary bytes (`COMP-3`, binary pointers).
- Python/Node scripts parse copybooks and display formatted record views.""",
        "solution": """### 1. View Records with VS Code Hex Editor
1. Install `ms-vscode.hexeditor` in VS Code.
2. In Zowe Explorer, right-click any dataset &rarr; **Open with... &rarr; Hex Editor**.
3. Inspect raw bytes side-by-side with EBCDIC text representation.

### 2. Format VSAM Records with Open-Source Copybook Mapper
Use a lightweight Python utility to inspect VSAM records overlaid with your COBOL copybook:
```python
from cobol_parser import parse_copybook, map_bytes_to_dict
import subprocess

# Download single record via Zowe CLI
raw_bytes = subprocess.check_output([
    "zowe", "zos-files", "download", "data-set", "PROD.KSDS.CUSTOMER", "--binary"
])

schema = parse_copybook("./copybooks/CUSTREC.cpy")
record = map_bytes_to_dict(raw_bytes[:250], schema)

for field, val in record.items():
    print(f"{field:<25}: {val}")
```
Output:
```text
CUST-ID                  : CUST-90214
CUST-NAME                : ACME CORPORATION
CUST-BALANCE             : $14,250.75 (COMP-3: X'1425075C')
```""",
        "prevention": [
            "De-install File Master Plus ISPF panel libraries (`CDBALOAD`) to remove license exposure.",
            "Train team members on VS Code Hex Editor keyboard shortcuts for binary editing.",
            "Use StackMF's open-source record mapper for formatted terminal outputs."
        ],
        "references": [
            {"title": "Visual Studio Marketplace: Microsoft Hex Editor", "url": "https://marketplace.visualstudio.com/items?itemName=ms-vscode.hexeditor"},
            {"title": "StackMF Broadcom License Replacement Hub", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },
    {
        "slug": "zowe-zosmf-rest-api-certificate-errors",
        "title": "Resolving SSL/TLS Certificate Untrusted and Handshake Errors in Zowe z/OSMF Connections",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["Zowe", "z/OSMF", "SSL", "TLS", "Certificates", "RACF", "Troubleshooting"],
        "reading_time": "10 min read",
        "tldr": "Zowe CLI and VS Code Zowe Explorer connections fail when z/OSMF presents a self-signed or enterprise internal root certificate. Learn how to export the z/OS CA certificate using RACF RACDCERT, import it into client truststores, and eliminate 'UNABLE_TO_VERIFY_LEAF_SIGNATURE' errors.",
        "problem": """Developers configuring Zowe CLI encounter blocking connection errors:
```text
Error: unable to verify the first certificate
code: UNABLE_TO_VERIFY_LEAF_SIGNATURE
Request failed to: https://zsys1.stackmf.internal:443/zosmf/restjobs/jobs
```
Developers add `rejectUnauthorized: false` as an insecure workaround, violating corporate security compliance.""",
        "root_cause": """By default, IBM z/OSMF uses a local self-signed certificate authority created during configuration (e.g. `zOSMFCA`).
Client operating systems (Windows, macOS, Linux) and Node.js do not trust internal mainframe CAs unless the root certificate is imported into the client truststore or specified in the Zowe profile.""",
        "solution": """### 1. Export the z/OSMF Certificate Authority from RACF
Have the security administrator issue:
```text
RACDCERT CERTAUTH EXPORT(LABEL('zOSMFCA')) -
         DSN('SYS1.ZOSMF.CACERT.DER') FORMAT(CERTDER)
```

### 2. Download Certificate to Local Machine via Binary Transfer
Transfer the exported DER file to your workstation and convert to PEM if needed:
```bash
zowe zos-files download data-set "SYS1.ZOSMF.CACERT.DER" --binary --file ./certs/zosmf-ca.cer
openssl x509 -inform der -in ./certs/zosmf-ca.cer -out ./certs/zosmf-ca.pem
```

### 3. Configure Zowe Profile to Trust the Mainframe CA
Update your `zowe.config.json` with the path to the trusted certificate:
```json
{
  "profiles": {
    "base": {
      "type": "base",
      "properties": {
        "host": "zsys1.stackmf.internal",
        "port": 443,
        "rejectUnauthorized": true,
        "ca": "./certs/zosmf-ca.pem"
      }
    }
  }
}
```
Now, all Zowe CLI and VS Code connections establish verified, hardened TLS 1.3 tunnels without certificate warnings!""",
        "prevention": [
            "Never deploy `--rejectUnauthorized false` in production or corporate laptops.",
            "Renew z/OSMF certificates before the standard 3-year expiration to prevent unexpected developer lockouts.",
            "Integrate z/OSMF with corporate Public Key Infrastructure (PKI) so standard enterprise root CAs sign mainframe certificates."
        ],
        "references": [
            {"title": "Open Mainframe Project: Configuring Zowe TLS Certificates", "url": "https://docs.zowe.org/stable/user-guide/configure-certificates"},
            {"title": "IBM z/OS Security Server RACF Command Reference: RACDCERT", "url": "https://www.ibm.com/docs/en/zos/latest?topic=commands-racdcert-manage-certificates"}
        ]
    },
    {
        "slug": "ezt-match-file-processing-imu-refactoring",
        "title": "Translating Easytrieve Synchronous File Match (MATCH Statement) into COBOL Two-Way Merge Logic",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Easytrieve", "MATCH Statement", "IMU", "COBOL", "File Merge", "Batch"],
        "reading_time": "10 min read",
        "tldr": "Easytrieve's native MATCH statement provides automated multi-file synchronization (matching master and transaction files). Discover how IMU converts MATCH statements into high-efficiency COBOL balanced line algorithms.",
        "problem": """An enterprise conversion from Easytrieve to COBOL encounters programs using:
```ezt
JOB INPUT (MASTER-FILE KEY (ACCT-NO) +
           TRANS-FILE KEY (ACCT-NO)) +
           MATCH (MASTER-FILE TRANS-FILE)
```
Manual developers struggle to replicate the exact Easytrieve match logic (duplicate keys, unmatched masters, orphan transactions), causing ledger reconciliation mismatches.""",
        "root_cause": """Easytrieve's `MATCH` statement implements a classic **Balanced-Line Algorithm**:
- Synchronously reads both files ordered by primary key.
- Handles match conditions automatically (`DUPLICATE`, `MATCHED`, `MASTER-ONLY`, `TRANS-ONLY`).
- IMU translates this into a deterministic COBOL evaluation loop with priming reads and high-value sentinel keys.""",
        "solution": """### 1. View IMU Emitted Balanced-Line COBOL Logic
IMU automatically emits standard COBOL merge logic:
```cobol
       PERFORM UNTIL WS-MASTER-EOF = 'Y' AND WS-TRANS-EOF = 'Y'
           EVALUATE TRUE
               WHEN WS-M-KEY = WS-T-KEY
                   PERFORM 2000-PROCESS-MATCHED-KEYS
                   PERFORM 1100-READ-TRANS-FILE
               WHEN WS-M-KEY < WS-T-KEY
                   PERFORM 2100-PROCESS-MASTER-ONLY
                   PERFORM 1000-READ-MASTER-FILE
               WHEN WS-M-KEY > WS-T-KEY
                   PERFORM 2200-PROCESS-TRANS-ONLY
                   PERFORM 1100-READ-TRANS-FILE
           END-EVALUATE
       END-PERFORM.
```

### 2. Handle Duplicate Keys Correctly
To ensure duplicate transaction keys are all processed against the same master record, the transaction file is read until `WS-T-KEY > WS-M-KEY` before advancing the master file pointer.

### 3. End-of-File High-Value Sentinel Pattern
When one file reaches EOF, set its key to `HIGH-VALUES` (`X'FF...FF'`):
```cobol
       READ MASTER-FILE
           AT END
               MOVE 'Y' TO WS-MASTER-EOF
               MOVE HIGH-VALUES TO WS-M-KEY
       END-READ.
```
This cleanly flushes remaining records from the other file without complex conditional branches!""",
        "prevention": [
            "Ensure both input files are pre-sorted on the match keys using DFSORT before executing merge logic.",
            "Verify duplicate key handling policies with business analysts prior to final cutover.",
            "Run automated regression tests comparing matched, unmatched, and dropped record counts."
        ],
        "references": [
            {"title": "IBM Migration Utility: Synchronous File Match Emulation", "url": "https://www.ibm.com/docs/en/imu/5.1.0"},
            {"title": "StackMF Enterprise Mainframe Modernization", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },
    {
        "slug": "vscode-debugger-for-mainframe-setup",
        "title": "Step-by-Step Configuration of the VS Code Debugger for Mainframe with IBM z/OS Debugger",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["VS Code", "Debugging", "IBM z/OS Debugger", "COBOL", "DevOps"],
        "reading_time": "10 min read",
        "tldr": "Bring modern visual debugging to VS Code. Learn how to configure launch.json, connect to the IBM z/OS Debugger headless service, and execute interactive source-level breakpoint debugging inside Visual Studio Code.",
        "problem": """Developers who have migrated to VS Code for code editing are still forced to switch to terminal sessions or 3270 green-screens whenever they need to debug a COBOL program step-by-step.""",
        "root_cause": """The **IBM Z Open Debug** extension enables the VS Code Debug Adapter Protocol (DAP) to communicate with the IBM z/OS Debugger on the mainframe over TCP/IP.""",
        "solution": """### 1. Install IBM Z Open Debug Extension
In VS Code, install `IBM.zopeneditor` and `IBM.z-open-debug`.

### 2. Configure `.vscode/launch.json`
Add the debug launch configuration:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "zopenedebug",
      "request": "launch",
      "name": "Debug Mainframe Batch COBOL",
      "port": 8001,
      "secure": false,
      "trace": true
    }
  ]
}
```

### 3. Launch Debug Session and Run Job
1. Press **F5** in VS Code to start listening on port 8001.
2. Submit your batch JCL with `//CEEOPTS DD` pointing to your IP:
   `TEST(ALL,*,PROMPT,TCPIP&<YOUR_IP>%8001:)`
3. When the job runs on z/OS, VS Code pauses execution, highlights the first line in yellow, and allows you to set visual breakpoints in the gutter!""",
        "prevention": [
            "Ensure workstation IP is reachable from the z/OS network (VPN/corporate LAN).",
            "Store compiler side-files (`SYSDEBUG`) in accessible libraries.",
            "Clean up completed debug sessions to release mainframe TCB threads."
        ],
        "references": [
            {"title": "IBM Z Open Debug Marketplace Extension", "url": "https://marketplace.visualstudio.com/items?itemName=IBM.zopenedebug"},
            {"title": "StackMF Modernization Bridge", "url": "https://stackmf.com/#fullstack-bridge"}
        ]
    },
    {
        "slug": "zowe-python-sdk-zos-automation-pipelines",
        "title": "Building Resilient Mainframe Automation Pipelines using the Zowe Python SDK",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["Zowe", "Python", "Automation", "SDK", "DevOps", "z/OS"],
        "reading_time": "10 min read",
        "tldr": "Automate complex mainframe administrative, deployment, and testing workflows in Python. Discover how to use the official Zowe Python SDK to manipulate datasets, submit batch jobs, issue console commands, and query system health programmatically.",
        "problem": """Shell scripts wrapping CLI tools can be brittle and hard to maintain when orchestrating multi-step mainframe workflows across multiple LPARs with error handling, retries, and database checks.""",
        "root_cause": """The **Zowe Python SDK (`zowe-sdk-python`)** provides native, typed Python client libraries for:
- Datasets & USS Files (`zowe.zos_files_for_zowe_sdk`)
- Batch Jobs (`zowe.zos_jobs_for_zowe_sdk`)
- TSO & System Console (`zowe.zos_console_for_zowe_sdk`)
- Workload Management & Sysplex Telemetry""",
        "solution": """### 1. Install the Zowe Python SDK
```bash
pip install zowe-sdk-python
```

### 2. Automate Job Submission and Spool Verification
```python
from zowe.zos_jobs_for_zowe_sdk import Jobs
from zowe.core_for_zowe_sdk import ProfileManager

# Load configuration from team profile
profile = ProfileManager().load(profile_name="zosmf")
jobs_client = Jobs(profile)

jcl_content = '''//TESTJOB  JOB (ACCT),'PYTHON TEST',CLASS=A,MSGCLASS=X
//STEP1    EXEC PGM=IEFBR14
'''

print("Submitting JCL via Zowe Python SDK...")
job = jobs_client.submit_from_string(jcl_content)
print(f"Submitted: {job.jobname} (ID: {job.jobid})")

# Wait for job completion
completed_job = jobs_client.wait_for_status(job.jobname, job.jobid, status="OUTPUT")
print(f"Job completed with Return Code: {completed_job.retcode}")

# Read Spool
spool_files = jobs_client.get_spool_files(job.jobname, job.jobid)
for sf in spool_files:
    print(f"Spool DD: {sf.ddname}, ID: {sf.stepname}")
```""",
        "prevention": [
            "Use context managers and exception handling (`ZoweError`) to trap network dropouts.",
            "Store authentication credentials using Zowe Secure Credential Store rather than hardcoded strings.",
            "Run automated test suites against isolated test LPARs."
        ],
        "references": [
            {"title": "Open Mainframe Project: Zowe Python SDK Documentation", "url": "https://github.com/zowe/zowe-client-python-sdk"},
            {"title": "StackMF Mainframe Engineering Pods", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },
    {
        "slug": "idz-carma-repository-ram-integration",
        "title": "Connecting IDz to Legacy SCM Repositories (CA Endevor, ChangeMan) using CARMA RAMs",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["IDz", "CARMA", "Endevor", "ChangeMan", "RAM", "DevOps"],
        "reading_time": "10 min read",
        "tldr": "If your organization hasn't yet completed the migration from CA Endevor or Serena ChangeMan to Git, use IBM CARMA (Common Access Repository Manager) inside IDz to check out, edit, and promote elements directly from the modern GUI without 3270 panels.",
        "problem": """Developers want to use the modern IDz editor but are still bound to 3270 green-screen panels to lock, check out, compile, and promote elements inside CA Endevor or ChangeMan ZMF.""",
        "root_cause": """IBM Developer for z/OS includes **CARMA (Common Access Repository Manager)**:
- CARMA connects to legacy software configuration managers through Repository Access Managers (RAMs).
- The Endevor RAM and ChangeMan RAM map mainframe packages, stages, and elements into tree views inside Eclipse/IDz.""",
        "solution": """### 1. Configure the CARMA Server on z/OS
Ensure the CARMA daemon (`CRASRV`) is running in `SYS1.PROCLIB`:
```jcl
//CRASRV   EXEC PGM=CRASTART,REGION=0M,
//  PARM='PORT=7535,TIMEOUT=300'
```

### 2. Connect from IDz CARMA Repositories View
1. In IDz, open the **CARMA Repositories** view.
2. Click **Add CARMA Connection**.
3. Select **CA Endevor SCM RAM** or **ChangeMan ZMF RAM**.
4. Enter your credentials. The entire Endevor inventory structure (Environment &rarr; Stage &rarr; System &rarr; Subsystem) appears as a navigable folder tree!

### 3. Check Out and Edit Elements
Right-click any COBOL element &rarr; **Extract to Project**. Edit in IDz, and right-click &rarr; **Check In / Generate** to trigger Endevor processors automatically!""",
        "prevention": [
            "Use CARMA as an interim bridge while planning full Git migration.",
            "Verify that CARMA RAM security exits enforce the same signout rules as native ISPF.",
            "Plan your eventual Endevor-to-Git cutover with StackMF's proven migration framework."
        ],
        "references": [
            {"title": "IBM Developer for z/OS: Working with CARMA", "url": "https://www.ibm.com/docs/en/developer-for-zos/latest?topic=repositories-carma"},
            {"title": "StackMF Turnkey Broadcom Endevor Replacement", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },
    {
        "slug": "ezt-printer-control-imu-asa-carriage-characters",
        "title": "Handling ANSI/ASA Carriage Control Characters in Easytrieve to IMU Migration",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Easytrieve", "IMU", "Carriage Control", "ASA", "Reporting", "COBOL"],
        "reading_time": "9 min read",
        "tldr": "Legacy mainframe reporting depends on Column 1 Carriage Control characters (ASA/ANSI: ' ', '0', '-', '1', '+'). Learn how to resolve page-eject discrepancies and printer alignment issues when migrating Easytrieve reports to COBOL using IBM Migration Utility.",
        "problem": """After migrating an Easytrieve batch program to COBOL via IMU, reports sent to production laser printers or digital report archive repositories (e.g. Mobius, CA-View/Deliver) print page headers across multiple pages or suppress form-feed page skips.""",
        "root_cause": """Mainframe print files use either:
- **ASA/ANSI Carriage Control (`RECFM=FBA` or `VBA`)**: Column 1 contains `' '` (Single space), `'0'` (Double space), `'-'` (Triple space), `'1'` (New page / Eject), `'+'` (Overstrike without advancing).
- **Machine Code Carriage Control (`RECFM=FBM` or `VBM`)**: Hex opcodes (`X'09'`, `X'89'`).

Easytrieve abstracts carriage control, emitting codes automatically.
If IMU's emitted COBOL specifies `WRITE ... AFTER ADVANCING` but the output DD statement or DCB is misconfigured, column 1 shifts, causing corrupt alignment.""",
        "solution": """### 1. Ensure RECFM=FBA on Output Datasets
In the execution JCL:
```jcl
//SYSPRINT DD DSN=PROD.REPORTS.BILLING,DISP=(NEW,CATLG,DELETE),
//            SPACE=(CYL,(10,5),RLSE),
//            DCB=(RECFM=FBA,LRECL=133,BLKSIZE=27930)
```
Notice `LRECL=133` (1 byte for carriage control + 132 print characters).

### 2. Configure IMU Carriage Control Mode in EZPARAMS
In `EZPARAMS`:
```text
PRT-CTRL=ASA
ADVANCING=AFTER
PAGE-EJECT=1
```

### 3. Validate Emitted COBOL WRITE Syntax
Ensure the generated COBOL uses standard advancing:
```cobol
       WRITE REPORT-RECORD FROM WS-PAGE-HEADER
           AFTER ADVANCING PAGE.
       WRITE REPORT-RECORD FROM WS-DETAIL-LINE
           AFTER ADVANCING 1 LINE.
```""",
        "prevention": [
            "Always inspect Column 1 in hexadecimal (`HEX ON` in ISPF) to verify valid ASA control characters.",
            "Ensure downstream archival software is configured for `FBA` recording formats.",
            "Verify that `LRECL` in COBOL `FD` matches JCL DCB `LRECL=133`."
        ],
        "references": [
            {"title": "IBM DFSMS Using Data Sets: Carriage Control Characters", "url": "https://www.ibm.com/docs/en/zos/latest?topic=formats-carriage-control-characters"},
            {"title": "IBM Migration Utility Reporting Manual", "url": "https://www.ibm.com/docs/en/imu/5.1.0"}
        ]
    },
    {
        "slug": "zowe-cli-secure-credential-store-plugin",
        "title": "Securing Enterprise Mainframe Credentials in CI/CD Runners using Zowe Secure Credential Store",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["Zowe CLI", "Security", "Credentials", "Vault", "CI/CD", "DevOps"],
        "reading_time": "9 min read",
        "tldr": "Never commit plaintext mainframe passwords to configuration files. Discover how to install and configure the Zowe Secure Credential Store plugin, integrate with OS keychains, and pass temporary secrets securely in automated GitHub Actions runners.",
        "problem": """Developers and automation scripts accidentally commit `zowe.config.json` containing unencrypted mainframe passwords to Git repositories, triggering security audits and credential revocations.""",
        "root_cause": """By default, Zowe CLI v2 stores non-secure properties in `zowe.config.json` and sensitive fields (passwords, private keys, client secrets) in the operating system's native secure credential vault via the `@zowe/secure-credential-store-for-zowe-cli` plugin.
If the plugin is missing or in headless Linux container environments without a graphical keychain (like GitHub Actions runners), credential lookups fail.""",
        "solution": """### 1. Install Secure Credential Store Plugin
```bash
zowe plugins install @zowe/secure-credential-store-for-zowe-cli
```

### 2. Secure Storage on Desktop (Windows / macOS)
When you run `zowe auth login`, Zowe stores passwords in:
- Windows: Windows Credential Manager
- macOS: Apple Keychain
- Linux Desktop: Secret Service / KWallet

### 3. Headless CI/CD Runners (GitHub Actions / Docker)
In headless Linux environments where no desktop keychain daemon exists, pass credentials dynamically via environment variables without modifying files:
```yaml
- name: Run Zowe Command in GitHub Actions
  env:
    ZOWE_OPT_HOST: ${{ secrets.ZOS_HOST }}
    ZOWE_OPT_USER: ${{ secrets.ZOS_USER }}
    ZOWE_OPT_PASSWORD: ${{ secrets.ZOS_PASSWORD }}
  run: |
    zowe zos-jobs list jobs --owner "$ZOWE_OPT_USER"
```""",
        "prevention": [
            "Add `zowe.config.user.json` to `.gitignore` to prevent private local overrides from being committed.",
            "Use automated pre-commit hooks (`git-secrets` or `trufflehog`) to block commits containing mainframe passwords.",
            "Rotate service account passwords every 90 days and manage via enterprise secrets managers."
        ],
        "references": [
            {"title": "Open Mainframe Project: Zowe Secure Credential Store", "url": "https://docs.zowe.org/stable/user-guide/cli-securingcredentials"},
            {"title": "StackMF DevOps & Broadcom Replacement Hub", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },
    {
        "slug": "vscode-mainframe-extension-pack-productivity",
        "title": "Maximizing Developer Velocity: Curating the Ultimate Mainframe Extension Pack for VS Code",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["VS Code", "Extensions", "Productivity", "DevOps", "Developer Tools"],
        "reading_time": "9 min read",
        "tldr": "Supercharge your mainframe engineering team. Explore the top essential extensions for Visual Studio Code: Zowe Explorer, COBOL Language Support, HLASM language servers, JCL formatters, and GitLens.",
        "problem": """New developers joining mainframe teams find the initial setup daunting, lacking a unified catalog of extensions and settings, leading to inconsistent development environments across the organization.""",
        "root_cause": """A cohesive development environment requires integrating multiple independent extensions:
- Storage & JES: Zowe Explorer
- Language Servers: COBOL, HLASM, REXX
- Build & Deploy: IBM Z Open Editor, GitLens
- Binary Inspection: Hex Editor""",
        "solution": """### 1. Recommended Extension Suite
Create `.vscode/extensions.json` in your repository:
```json
{
  "recommendations": [
    "Zowe.vscode-extension-for-zowe",
    "IBM.ibm-zopeneditor",
    "che-incubator.cobol-language-support",
    "BroadcomMFD.hlasm-language-support",
    "rexx-language-support.rexx",
    "ms-vscode.hexeditor",
    "eamodio.gitlens"
  ]
}
```

### 2. Configure Unified Workspace Settings
In `.vscode/settings.json`:
```json
{
  "editor.rulers": [7, 8, 72, 80],
  "editor.tabSize": 4,
  "editor.insertSpaces": true,
  "files.associations": {
    "*.cbl": "cobol",
    "*.cpy": "cobol",
    "*.jcl": "jcl",
    "*.rexx": "rexx"
  }
}
```
Setting `editor.rulers` to columns 7, 8, 72, and 80 ensures developers visually adhere to traditional COBOL area margins!""",
        "prevention": [
            "Use VS Code Workspace files (`.code-workspace`) to standardize settings across your engineering pod.",
            "Leverage GitHub Codespaces or Dev Containers for instant zero-install browser-based mainframe onboarding.",
            "Keep extensions updated to benefit from upstream Zowe and LSP performance improvements."
        ],
        "references": [
            {"title": "Open Mainframe Project: Getting Started with VS Code", "url": "https://www.openmainframeproject.org"},
            {"title": "StackMF Mainframe Full-Stack Developer Hiring Pods", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },
    {
        "slug": "zowe-containers-openshift-kubernetes-deployment",
        "title": "Deploying Zowe Server Components on Red Hat OpenShift and Kubernetes for Hybrid Cloud",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Zowe", "Kubernetes", "OpenShift", "Containers", "Hybrid Cloud", "Modernisation"],
        "reading_time": "11 min read",
        "tldr": "Offload compute and simplify Zowe administration by running Zowe server components (APIML, Discovery, Desktop, Caching) inside containerized Red Hat OpenShift or Kubernetes clusters while maintaining secure cross-memory connections to z/OS.",
        "problem": """Running all Zowe server address spaces directly on z/OS consumes valuable general-purpose engine capacity and memory, leading to concerns from system programmers regarding z/OS LPAR footprint.""",
        "root_cause": """While low-level services (Cross-Memory Server) must execute on z/OS, higher-level services (Zowe API Mediation Layer, Gateway, Web Desktop, Discovery Server) are Java and Node.js microservices.
**Zowe for Kubernetes/OpenShift**:
- Packages these services into OCI-compliant container images.
- Deploys them onto commodity cloud/on-premise Kubernetes clusters.
- Offloads 80%+ of Zowe's compute overhead away from billable mainframe MSU/MIPS!""",
        "solution": """### 1. Deploy via Helm Chart
Configure `values.yaml` for your Kubernetes cluster:
```yaml
zowe:
  domain: zowe.cloud.stackmf.internal
  endpoint:
    host: zsys1.stackmf.internal
    port: 7554
  components:
    gateway:
      replicas: 2
    discovery:
      replicas: 2
    cachingService:
      storage: 5Gi
```
Deploy the Helm release:
```bash
helm install zowe-core oci://zowe-docker-release.jfrog.io/helm/zowe -f values.yaml --namespace zowe --create-namespace
```

### 2. Verify Pod Health on OpenShift
```bash
oc get pods -n zowe
```
Output:
```text
NAME                                READY   STATUS    RESTARTS   AGE
zowe-api-gateway-6d849b4c-2x9la     1/1     Running   0          5m
zowe-discovery-service-7f99b-4k2ml  1/1     Running   0          5m
zowe-caching-service-592b8-9p11z    1/1     Running   0          5m
```

### 3. Connect to z/OS Subsystems
The containerized gateway establishes outbound mTLS connections to z/OSMF and CICS on z/OS, delivering blazing-fast API routing without consuming mainframe CPU!""",
        "prevention": [
            "Implement high-availability pod replicas across multiple Kubernetes worker nodes.",
            "Use enterprise ingress controllers with automated Let's Encrypt / corporate TLS certificates.",
            "Establish network security policies allowing egress traffic only to verified z/OS IP ranges."
        ],
        "references": [
            {"title": "Open Mainframe Project: Zowe on Kubernetes Documentation", "url": "https://docs.zowe.org/stable/user-guide/k8s-introduction"},
            {"title": "StackMF Mainframe Modernization Architecture", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },

    # =========================================================================
    # PART 2: COBOL, DB2, CICS, VSAM, IMS, CA-7, TELON, REXX, ENDEVOR,
    #         CHANGEMAN, ABENDS & PERFORMANCE (25 ARTICLES)
    # =========================================================================
    {
        "slug": "s0c9-fixed-point-divide-exception-cobol",
        "title": "Troubleshooting ABEND S0C9 (Fixed-Point Divide Exception) in COBOL Financial Calculations",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["COBOL", "ABEND S0C9", "Divide by Zero", "CEEDUMP", "Financial Math"],
        "reading_time": "9 min read",
        "tldr": "ABEND S0C9 occurs when an arithmetic statement attempts to divide by zero or when the quotient of a division exceeds the capacity of the target binary/packed-decimal field. Learn how to trap divide errors with ON SIZE ERROR and analyze CEEDUMP stack frames.",
        "problem": """An overnight interest-accrual batch step terminates abruptly:
```text
SYSTEM COMPLETION CODE=0C9  REASON CODE=00000009
PSW AT TIME OF INTERRUPT: 078D1000 84001F12  ILC 4  INTC 09
CEE3209S The system detected a fixed-point divide exception.
         From compile unit FINCALC at statement 612.
```
The batch stream crashes, leaving loan interest tables unposted.""",
        "root_cause": """The z/Architecture hardware raises Interrupt Code 09 (Fixed-Point Divide Exception) when:
1. **Division by Zero**: The divisor variable evaluated to zero (`DIVIDE WS-TOTAL-INTEREST BY WS-MONTH-COUNT`, where `WS-MONTH-COUNT = 0`).
2. **Quotient Overflow**: In binary integer division (`DP` or `DR` instruction), the resulting quotient is too large to fit in the quotient register or defined variable.""",
        "solution": """### 1. Check CEEDUMP Local Variables
Open CEEDUMP and inspect statement 612 variables:
```text
WS-MONTH-COUNT: 0000 (Divisor is ZERO!)
WS-TOTAL-INTEREST: +00014250.25
```

### 2. Implement ON SIZE ERROR Clause
Never execute division without an `ON SIZE ERROR` defensive handler:
```cobol
       DIVIDE WS-TOTAL-INTEREST BY WS-MONTH-COUNT
           GIVING WS-AVG-MONTHLY-INTEREST
           ROUNDED
           ON SIZE ERROR
               PERFORM 9100-HANDLE-ZERO-DIVISOR
           NOT ON SIZE ERROR
               PERFORM 2000-POST-INTEREST
       END-DIVIDE.
```

### 3. Pre-Validate Divisor Prior to Computation
```cobol
       IF WS-MONTH-COUNT > 0
           COMPUTE WS-AVG-MONTHLY-INTEREST ROUNDED =
               WS-TOTAL-INTEREST / WS-MONTH-COUNT
       ELSE
           MOVE 0 TO WS-AVG-MONTHLY-INTEREST
           PERFORM 9200-LOG-DATA-ANOMALY
       END-IF.
```""",
        "prevention": [
            "Always include `ON SIZE ERROR` on all `DIVIDE` and `COMPUTE` statements.",
            "Verify input feeds from web APIs or flat files to ensure divisor columns are populated.",
            "Size receiving fields generously to prevent quotient overflow."
        ],
        "references": [
            {"title": "IBM z/OS MVS System Codes: Completion Code 0C9", "url": "https://www.ibm.com/docs/en/zos/latest?topic=codes-0c9"},
            {"title": "IBM Enterprise COBOL: Handling Arithmetic Exceptions", "url": "https://www.ibm.com/docs/en/cobol-zos/latest?topic=statements-divide"}
        ]
    },
    {
        "slug": "s806-load-module-not-found-steplib-debugging",
        "title": "Diagnosing ABEND S806-04: Resolving Missing Load Modules in JOBLIB, STEPLIB, and LPA",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["JCL", "ABEND S806", "STEPLIB", "JOBLIB", "Link-Edit", "Binder"],
        "reading_time": "8 min read",
        "tldr": "ABEND S806 (Reason 04) indicates the MVS program fetch mechanism searched all designated libraries (STEPLIB, JOBLIB, LPA, LNKLST) but could not locate the requested program member. Discover search order hierarchy and resolution techniques.",
        "problem": """A newly promoted production batch job fails immediately at step initiation:
```text
CSV003I REQUESTED MODULE MODPAY01 NOT FOUND
CSV028I JOBPAY01 STEP010 - ABEND=S806 U0000 REASON=00000004
IEF450I JOBPAY01 STEP010 - ABEND=S806 U0000
```
No code executed; the step terminated during job initiator program fetch.""",
        "root_cause": """When z/OS initiates a step (`EXEC PGM=MODPAY01`):
1. It searches private step libraries: `//STEPLIB DD`.
2. It searches job-level libraries: `//JOBLIB DD`.
3. It searches Link Pack Area (LPA / MLPA / FLPA).
4. It searches system link list: `LNKLST` (`SYS1.LINKLIB`, etc.).
If member `MODPAY01` is absent, misspelled, un-cataloged, or the load dataset has allocation security restrictions, MVS raises S806-04.""",
        "solution": """### 1. Verify STEPLIB Concatenation in JCL
Ensure the dataset containing the compiled load module is in the `STEPLIB`:
```jcl
//STEP010  EXEC PGM=MODPAY01
//STEPLIB  DD DSN=PROD.APPLICATION.LOADLIB,DISP=SHR
//         DD DSN=CEE.SCEERUN,DISP=SHR
```

### 2. Verify Member Presence via ISPF / TSO
In ISPF 3.4, browse `PROD.APPLICATION.LOADLIB`:
- Check if member `MODPAY01` exists.
- Check if member was saved as non-executable (`NOEXEC`) due to Binder errors during compilation.

### 3. Check Dynamic LNKLST Updates
If the module was deployed to a system LNKLST dataset, update the catalog cache:
```text
/SETPROG LNKLST,UNALLOCATE
/SETPROG LNKLST,ALLOCATE
```""",
        "prevention": [
            "Include `CEE.SCEERUN` and `CEE.SCEERUN2` in standard `STEPLIB` concatenations.",
            "Verify Binder Return Code was 0 or 4 during compile/link steps in CI/CD.",
            "Prevent naming discrepancies between Endevor element names and Binder output member names."
        ],
        "references": [
            {"title": "IBM z/OS MVS System Codes: Completion Code 806", "url": "https://www.ibm.com/docs/en/zos/latest?topic=codes-806"},
            {"title": "IBM z/OS MVS Initialization and Tuning: Search Order for Programs", "url": "https://www.ibm.com/docs/en/zos/latest?topic=libraries-program-search-order"}
        ]
    },
    {
        "slug": "s322-s222-cpu-time-limit-batch-abends",
        "title": "Fixing ABEND S322 (CPU Time Limit Exceeded) and S222 (Job Cancelled) in Long-Running Batch",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["JCL", "ABEND S322", "ABEND S222", "TIME Parameter", "Batch Optimization"],
        "reading_time": "9 min read",
        "tldr": "ABEND S322 occurs when a batch job exceeds its allocated CPU time limit (due to an infinite loop, massive dataset scans, or inadequate JCL TIME parameters). Learn how to tune TIME parameters, optimize loops, and handle S222 operator cancellations.",
        "problem": """An overnight database rebuild job runs for 4 hours and crashes:
```text
IEF373I STEP /STEP020 / START 2026270.0100
IEF374I STEP /STEP020 / STOP  2026270.0500 CPU   240MIN 00.12SEC
IEF450I DBREBD01 STEP020 - ABEND=S322 U0000 REASON=00000000
```
Database indexes are left in rebuild-pending state, blocking morning online transaction systems.""",
        "root_cause": """- **ABEND S322**: The job step consumed more CPU time than authorized by the JCL `TIME` parameter or system SMF default (`JWT` / Job Wait Time in `SMFPRMxx`).
- **ABEND S222**: The system operator or an automated console monitor issued the `CANCEL` command against the job due to excessive execution duration or lock blocking.""",
        "solution": """### 1. Increase JCL TIME Parameter
For legitimately long-running batch extraction or utility jobs, specify sufficient CPU time:
```jcl
//STEP020  EXEC PGM=DBREBD01,TIME=(600,00)
```
- `TIME=(600,00)`: Grants 600 CPU minutes (10 hours) and 00 seconds.
- `TIME=1440` or `TIME=NOLIMIT`: Disables the job CPU timer completely (use with caution).

### 2. Isolate Infinite Loops in Program Code
If the program should execute in 5 minutes but burns hours:
1. Examine the program PSW in the dump.
2. Check for missing read advances in `PERFORM UNTIL` loops:
```cobol
      * BAD: Never reads next record inside loop!
       PERFORM UNTIL WS-EOF = 'Y'
           PERFORM 2000-PROCESS-DATA
      * MISSING: READ INPUT-FILE AT END MOVE 'Y' TO WS-EOF
       END-PERFORM.
```

### 3. Add Intermediate Checkpoint Commits
Ensure long-running batch jobs commit periodically to avoid lock contention that triggers operator cancellations.""",
        "prevention": [
            "Never specify `TIME=1440` on untested batch programs.",
            "Monitor SMF Type 30 records to establish historical CPU run-time baselines.",
            "Use automated alerts when batch jobs exceed 2x their standard historical elapsed time."
        ],
        "references": [
            {"title": "IBM z/OS MVS JCL Reference: TIME Parameter", "url": "https://www.ibm.com/docs/en/zos/latest?topic=parameters-time-parameter"},
            {"title": "IBM z/OS MVS System Codes: Completion Code 322", "url": "https://www.ibm.com/docs/en/zos/latest?topic=codes-322"}
        ]
    },
    {
        "slug": "s878-s80a-out-of-virtual-storage-abends",
        "title": "Resolving ABEND S878 & S80A: Virtual Storage Exhaustion in 24-bit and 31-bit z/OS Memory",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["Memory", "ABEND S878", "ABEND S80A", "GETMAIN", "REGION", "Below-the-Bar"],
        "reading_time": "10 min read",
        "tldr": "ABEND S878 and S80A indicate that an MVS GETMAIN or Language Environment heap allocation failed because below-the-bar virtual storage (24-bit/31-bit) was exhausted. Discover how to tune JCL REGION parameters and compile with RMODE(ANY) and LP(64).",
        "problem": """A batch report processing 5 million transactions fails:
```text
IEA705I ERROR DURING GETMAIN SYS CODE = 878-10 JOBPAY01 STEP030
IEF450I JOBPAY01 STEP030 - ABEND=S878 U0000 REASON=00000010
```
Or with `ABEND=S80A Reason 10` during subpool allocation. Increasing `REGION=64M` does not resolve the issue.""",
        "root_cause": """In z/Architecture:
- **24-bit Storage (Below the Line)**: Exactly 16 Megabytes. Shared by MVS nucleus, access method buffers (QSAM/VSAM), and legacy 24-bit programs.
- **31-bit Storage (Below the Bar)**: Up to 2 Gigabytes.
- **Reason Code 10**: Virtual storage unavailable in private area.
If programs are compiled with `AMODE(24),RMODE(24)` or open hundreds of files simultaneously, the 16MB line saturates, causing S878 even if gigabytes of physical RAM exist!""",
        "solution": """### 1. Compile Programs with AMODE(31) and RMODE(ANY)
Move program load modules above the 16MB line:
```jcl
//COBSTEP EXEC PGM=IGYCRCTL,
//  PARM='OPT(2),ARCH(14),AMODE(31),RMODE(ANY)'
```

### 2. Configure Proper JCL REGION Parameter
Set `REGION=0M` or `REGION=128M`:
```jcl
//STEP030  EXEC PGM=MODPAY01,REGION=0M
```
`REGION=0M` grants the maximum available storage above and below the 16MB line in the private area.

### 3. Tune Language Environment HEAP Options
Move LE runtime heap above the 16MB line:
```jcl
//CEEOPTS  DD *
  HEAP(64M,16M,ANYWHERE,KEEP),
  STORAGE(NONE,NONE,NONE,0K),
  STACK(128K,128K,ANYWHERE,KEEP)
/*
```
Specifying `ANYWHERE` forces dynamic allocations into 31-bit storage, completely freeing the 16MB line.""",
        "prevention": [
            "Never compile new applications with `RMODE(24)`.",
            "Avoid holding thousands of files open concurrently in a single COBOL run unit; close files when processing finishes.",
            "Migrate large in-memory lookup arrays to 64-bit memory objects (`LP(64)`)."
        ],
        "references": [
            {"title": "IBM z/OS MVS System Codes: Completion Code 878", "url": "https://www.ibm.com/docs/en/zos/latest?topic=codes-878"},
            {"title": "IBM Language Environment Customization: HEAP Settings", "url": "https://www.ibm.com/docs/en/zos/latest?topic=descriptions-heap"}
        ]
    },
    {
        "slug": "cics-aeyh-abend-db2-connection-failure",
        "title": "Resolving CICS AEYH ABEND: CICS-DB2 Attachment Facility Disconnects and Thread Pool Starvation",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["CICS", "DB2", "ABEND AEYH", "Attachment Facility", "Threads", "DB2CONN"],
        "reading_time": "10 min read",
        "tldr": "CICS ABEND AEYH occurs when an application issues an EXEC SQL statement but the CICS-DB2 attachment facility is inactive or when all pool threads are exhausted. Learn how to diagnose DB2CONN and DB2ENTRY resources and tune thread limits.",
        "problem": """Every CICS transaction attempting to access DB2 tables crashes simultaneously:
```text
DFHAC2206 09:12:04 CICS01 TRANSACTION TXIN ABENDED AEYH IN PROGRAM CUSTINQ.
          THE CICS DB2 ATTACHMENT FACILITY IS NOT CONNECTED.
```
Online customer portals return HTTP 500 errors across all digital banking channels.""",
        "root_cause": """The CICS-to-DB2 interface is managed by the CICS DB2 Attachment Facility:
1. **DB2 Subsystem Disconnected**: DB2 was recycled or crashed, or the attachment was disconnected via `DSNC DISCONNECT`.
2. **Thread Starvation**: The transaction's `DB2ENTRY` reached its `THREADLIMIT`, and `THREADWAIT=NO` was specified, forcing an immediate AEYH rejection.
3. **Plan Authorization Failure**: The CICS user lacks `EXECUTE` authority on the DB2 application plan.""",
        "solution": """### 1. Inquire and Start the CICS-DB2 Connection
From the CICS master terminal:
```text
CEMT INQUIRE DB2CONN
```
If `STATUS: DISCONNECTED`, issue:
```text
CEMT SET DB2CONN CONNECTED
```
Or via the DB2 operator interface:
```text
DSNC STRT DB2P
```

### 2. Configure DB2ENTRY Thread Overflow
In the CICS System Definition (CSD), configure thread pool overflow so transactions wait or overflow to general pool threads rather than abending:
```text
CEDA DEFINE DB2ENTRY(TXINENT) GROUP(BANKGRP)
     TRANSID(TXIN)
     PLAN(PLNBANK1)
     THREADLIMIT(25)
     THREADWAIT(YES)
```
- `THREADWAIT(YES)`: If all 25 threads are active, incoming requests queue smoothly instead of crashing with AEYH.

### 3. Handle AEYH in Application Code
Add error handling around SQL calls:
```cobol
       EXEC SQL
           SELECT CUST_NAME INTO :WS-CUST-NAME
           FROM CUSTOMER WHERE CUST_ID = :WS-CUST-ID
       END-EXEC.

       IF SQLCODE = -922 OR SQLCODE = -924
           MOVE 'DB2 Subsystem Offline - Try Again Later'
             TO WS-USER-MESSAGE
           EXEC CICS RETURN END-EXEC
       END-IF.
```""",
        "prevention": [
            "Configure automatic reconnection in `DB2CONN` (`STANDBYMODE=RECONNECT`).",
            "Monitor CICS DB2 statistics (`DSNC DISP STAT`) during peak hours to right-size thread pools.",
            "Ensure DB2 maintenance windows coordinate automatic CICS connection cycling."
        ],
        "references": [
            {"title": "IBM CICS TS: Connecting to Db2 for z/OS", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=db2-connecting-cics-db2"},
            {"title": "IBM CICS TS: DB2CONN and DB2ENTRY Attributes", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=definitions-db2conn-attributes"}
        ]
    },
    {
        "slug": "db2-sqlcode-803-duplicate-key-violation",
        "title": "Handling DB2 SQLCODE -803: Unique Index Constraint Violations in Concurrent Batch Inserts",
        "date": "2026-09-27",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "SQLCODE -803", "Unique Index", "Constraints", "Concurrency"],
        "reading_time": "9 min read",
        "tldr": "DB2 SQLCODE -803 indicates an INSERT or UPDATE statement violated a unique index constraint. Discover strategies to diagnose conflicting keys, use MERGE statements, and implement SELECT FOR UPDATE patterns.",
        "problem": """Concurrent transaction ingestion jobs fail in overnight batch:
```text
DSNT408I SQLCODE = -803, ERROR:  ONE OR MORE VALUES IN THE INSERT OR UPDATE
         STATEMENT ARE NOT VALID BECAUSE THE OBJECT TABLE WOULD VIOLATE
         PRIMARY OR UNIQUE KEY CONSTRAINT 'DSN8D13A.CUST_UNQ_IDX'
DSNT418I SQLSTATE = 23505 SQLSTATE RETURN CODE
```
The job halts, rolling back earlier batch inserts.""",
        "root_cause": """A table has a unique index (`CREATE UNIQUE INDEX CUST_UNQ_IDX ON CUSTOMER (ACCT_NO)`):
- Two concurrent worker jobs attempt to insert records with the same primary key.
- A batch file contains duplicate records within the same input stream.
- An identity column sequence or generator cycle was reset incorrectly.""",
        "solution": """### 1. Identify Conflicting Key Values
Inspect the input record that triggered the failure or run diagnostic query:
```sql
SELECT ACCT_NO, COUNT(*)
FROM INCOMING_STAGE_TABLE
GROUP BY ACCT_NO
HAVING COUNT(*) > 1;
```

### 2. Implement SQL MERGE (UPSERT) Syntax
Replace separate `INSERT` statements with an atomic `MERGE`:
```sql
MERGE INTO CUSTOMER AS C
USING (VALUES (:WS-ACCT-NO, :WS-NAME, :WS-BAL)) AS S(ACCT_NO, NAME, BAL)
ON C.ACCT_NO = S.ACCT_NO
WHEN MATCHED THEN
    UPDATE SET C.BALANCE = S.BAL, C.NAME = S.NAME
WHEN NOT MATCHED THEN
    INSERT (ACCT_NO, NAME, BALANCE)
    VALUES (S.ACCT_NO, S.NAME, S.BAL);
```

### 3. Handle -803 Gracefully in COBOL Logic
```cobol
       EXEC SQL
           INSERT INTO CUSTOMER VALUES (:WS-CUST-RECORD)
       END-EXEC.

       IF SQLCODE = -803
      * Key already exists - update existing record instead
           PERFORM 3000-UPDATE-EXISTING-CUSTOMER
       ELSE
           IF SQLCODE NOT = 0
               PERFORM 9999-DB2-ERROR
           END-IF
       END-IF.
```""",
        "prevention": [
            "Run DFSORT `SUM FIELDS=NONE` on incoming batch files to deduplicate records prior to database ingestion.",
            "Use generated DB2 sequences with `NO CYCLE` for surrogate primary keys.",
            "Leverage atomic `MERGE` statements to eliminate race conditions between concurrent worker threads."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS Codes: SQLCODE -803", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=codes-803"},
            {"title": "IBM Db2 13 for z/OS SQL Reference: MERGE Statement", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=statements-merge"}
        ]
    },
    {
        "slug": "db2-sqlcode-818-timestamp-consistency-token",
        "title": "Resolving DB2 SQLCODE -818: Precompiler Timestamp Token Mismatch Between Plan and Load Module",
        "date": "2026-09-27",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "SQLCODE -818", "Consistency Token", "Precompiler", "BIND PACKAGE", "DevOps"],
        "reading_time": "9 min read",
        "tldr": "DB2 SQLCODE -818 occurs when the consistency token (timestamp) embedded in the compiled COBOL load module does not match the token in the bound DB2 package. Learn how to verify timestamps and ensure atomic compile/bind automation.",
        "problem": """After promoting a bugfix load module to production, users executing the transaction receive:
```text
DSNT408I SQLCODE = -818, ERROR:  THE PRECOMPILER-GENERATED TIMESTAMP OR
         CONTOKEN IN THE LOAD MODULE IS NOT EQUAL TO THE TIMESTAMP
         GENERATED IN THE DBRM BIND PACKAGE 'DSN8D13A.CUST01'
DSNT418I SQLSTATE = 51015 SQLSTATE RETURN CODE
```
The transaction refuses to execute, paralyzing operations.""",
        "root_cause": """When a COBOL program with embedded SQL is compiled:
1. The DB2 Precompiler (or integrated coprocessor) generates a 24-byte **Consistency Token (CONTOKEN)** based on the exact compile timestamp.
2. The precompiler writes this token into both the DBRM (Database Request Module) and the emitted COBOL Working-Storage.
3. At execution time, DB2 compares the token inside the load module with the token in `SYSIBM.SYSPACKAGE`.
4. If someone compiled the program twice but bound the DBRM from the first compile, the tokens mismatch, triggering SQLCODE -818.""",
        "solution": """### 1. Compare Consistency Tokens in Load Module and Catalog
Run AMBLIST to view the token in the load module:
```jcl
//STEP1    EXEC PGM=AMBLIST
//SYSPRINT DD SYSOUT=*
//LOADLIB  DD DSN=PROD.LOADLIB,DISP=SHR
//SYSIN    DD *
  LISTIDR MEMBER=CUST01
/*
```
Query the consistency token in the DB2 catalog:
```sql
SELECT NAME, HEX(CONTOKEN), BIND_TIME
FROM SYSIBM.SYSPACKAGE
WHERE NAME = 'CUST01';
```

### 2. Rebind the Package from the Correct DBRM
Rebind using the DBRM produced during the exact same compile run:
```text
BIND PACKAGE(DSN8D13A) -
     MEMBER(CUST01) -
     ACTION(REPLACE) -
     ISOLATION(CS)
```

### 3. Alternative: Precompile with Explicit CONTOKEN
In automated CI/CD pipelines, specify a deterministic token:
```jcl
//COBSTEP EXEC PGM=IGYCRCTL,
//  PARM='SQL(CONTOKEN(GITCOMMITSHA))'
```""",
        "prevention": [
            "Never separate compile and bind steps across uncoordinated manual jobs.",
            "Use IBM Dependency Based Build (DBB) or Git CI/CD to atomically bind DBRMs immediately after compilation.",
            "Ensure automated deployment packages promote both the load module and the package bind simultaneously."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS Codes: SQLCODE -818", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=codes-818"},
            {"title": "IBM Db2 13 for z/OS Application Programming: Consistency Tokens", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=programming-consistency-tokens"}
        ]
    },
    {
        "slug": "db2-sqlcode-501-502-cursor-state-errors",
        "title": "Fixing DB2 SQLCODE -501 (Cursor Not Open) and SQLCODE -502 (Cursor Already Open) in Nested Calls",
        "date": "2026-09-27",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "SQLCODE -501", "SQLCODE -502", "Cursors", "COBOL", "Stored Procedures"],
        "reading_time": "8 min read",
        "tldr": "DB2 SQLCODE -501 occurs when attempting to FETCH from or CLOSE a cursor that is closed. SQLCODE -502 occurs when OPENing an already open cursor. Learn how to manage cursor states across nested subprogram calls and commit boundaries.",
        "problem": """A complex batch billing cycle terminates with:
```text
DSNT408I SQLCODE = -501, ERROR:  THE CURSOR IDENTIFIED IN A FETCH OR CLOSE
         STATEMENT IS NOT OPEN. CURSOR NAME = CUST_CSR
```
Or in a loop:
```text
DSNT408I SQLCODE = -502, ERROR:  THE CURSOR IDENTIFIED IN AN OPEN STATEMENT
         IS ALREADY OPEN. CURSOR NAME = CUST_CSR
```""",
        "root_cause": """1. **SQLCODE -501**:
   - The cursor was closed automatically when an intervening `COMMIT` was issued without `WITH HOLD`.
   - The cursor hit `SQLCODE = +100` (End of Table) and the application issued `FETCH` again.
2. **SQLCODE -502**:
   - An application called subprogram `SUB1` multiple times without closing the cursor prior to `GOBACK`.
   - A loop re-executed `EXEC SQL OPEN CUST_CSR END-EXEC` without a prior `CLOSE`.""",
        "solution": """### 1. Declare Cursors WITH HOLD Across Commits
If a batch program issues commits while iterating through a cursor:
```cobol
       EXEC SQL
           DECLARE CUST_CSR CURSOR WITH HOLD FOR
           SELECT CUST_ID, BALANCE
           FROM CUSTOMER
           WHERE REGION = :WS-REGION
       END-EXEC.
```
`WITH HOLD` keeps the cursor open and maintains its position across `EXEC SQL COMMIT` calls!

### 2. Defensively Manage Cursor State in Subprograms
Track cursor open status in Working-Storage:
```cobol
       IF WS-CSR-IS-OPEN = 'N'
           EXEC SQL OPEN CUST_CSR END-EXEC
           MOVE 'Y' TO WS-CSR-IS-OPEN
       END-IF.

       EXEC SQL FETCH CUST_CSR INTO :WS-CUST-ROW END-EXEC.

       IF SQLCODE = 100
           EXEC SQL CLOSE CUST_CSR END-EXEC
           MOVE 'N' TO WS-CSR-IS-OPEN
       END-IF.
```""",
        "prevention": [
            "Always include `WITH HOLD` on cursors that process multi-commit batch update windows.",
            "Always close open cursors before exiting subprograms.",
            "Inspect `SQLCODE` immediately after every `OPEN`, `FETCH`, and `CLOSE`."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS SQL Reference: DECLARE CURSOR", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=statements-declare-cursor"},
            {"title": "IBM Db2 13 for z/OS Codes: SQLCODE -501 and -502", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=codes-501"}
        ]
    },
    {
        "slug": "cics-aica-excessive-loop-dispatcher-tuning",
        "title": "Advanced CICS AICA Tuning: Calculating CPU Dispatch Loops and SIT RUNAWAY Thresholds",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["CICS", "AICA", "SIT", "RUNAWAY", "Dispatcher", "Performance"],
        "reading_time": "10 min read",
        "tldr": "Deep architectural analysis of CICS transaction runaway timer mechanics. Learn how the CICS dispatcher calculates interval control timer ticks, how to calibrate SIT ICV and RUNAWAY thresholds, and how to analyze MVS system trace tables to isolate tight machine code loops.",
        "problem": """During peak end-of-quarter volume, high-value CICS transactions terminate with ABEND AICA. System programmers debate whether the transaction contains an infinite loop or if extreme DASD/CPU contention caused legitimate business calculations to exceed the default 5-second runaway interval.""",
        "root_cause": """The CICS Task Dispatcher monitors tasks executing on the Quasi-Reentrant (QR) or Open TCBs:
- Every time a task yields control via a CICS command, its runaway timer resets to zero.
- If a task executes contiguous application instructions without yielding for longer than the `RUNAWAY` limit, CICS flags it as a runaway task and abends it with AICA to prevent starvation of other concurrent tasks.""",
        "solution": """### 1. Calibrate SIT RUNAWAY Parameter
In the System Initialization Table (SIT):
```text
RUNAWAY=5000
```
(Interval in milliseconds, default 5000 = 5 seconds).

### 2. Configure Specific Transactions for Extended Limits
For CPU-heavy analytic or encryption transactions, override the SIT default in the CSD:
```text
CEDA DEFINE TRANSACTION(TXAN) GROUP(FINAPP)
     PROGRAM(ANALYT01)
     RUNAWAY(15000)
```
Allows up to 15 seconds of contiguous execution.

### 3. Insert Programmatic Dispatcher Yields
In COBOL programs performing heavy matrix multiplication or large table parsing:
```cobol
       ADD 1 TO WS-PROCESSED-COUNT
       IF WS-PROCESSED-COUNT > 2000
           EXEC CICS SUSPEND END-EXEC
           MOVE 0 TO WS-PROCESSED-COUNT
       END-IF.
```
`EXEC CICS SUSPEND` causes the task to give up control to other waiting tasks and immediately resets the runaway timer!""",
        "prevention": [
            "Never set `RUNAWAY=0` (disabled) across an entire CICS region; this leaves regions vulnerable to total freeze.",
            "Use CICS performance class monitoring records (SMF 110) to profile transaction CPU distribution.",
            "Offload CPU-heavy computation to asynchronous background batch or zIIP-eligible Java routines."
        ],
        "references": [
            {"title": "IBM CICS TS: Dealing with Runaway Tasks", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=dumps-investigating-aica-abend"},
            {"title": "IBM CICS TS: System Initialization Table RUNAWAY Parameter", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=parameters-runaway"}
        ]
    },
    {
        "slug": "vsam-file-status-35-missing-dataset-jcl",
        "title": "Troubleshooting VSAM File Status 35: Dataset Not Found during Dynamic Allocation in Batch & CICS",
        "date": "2026-09-27",
        "category": "CICS & VSAM Architecture",
        "tags": ["VSAM", "File Status 35", "COBOL", "JCL", "Dynamic Allocation", "CICS"],
        "reading_time": "8 min read",
        "tldr": "VSAM File Status 35 indicates that an OPEN statement failed because the designated physical dataset does not exist or was not found in the master/user catalog. Learn how to verify catalog pointers, fix dynamic allocation parameters, and handle optional files.",
        "problem": """A daily batch reporting job abends on statement 102:
```text
PROG01: OPEN ERROR FOR FILE 'CUSTVSAM'
FILE STATUS = 35
CEE3250C The system or user abend U4038 was issued.
```
The developer insists the DD card exists in the JCL, yet the job refuses to run.""",
        "root_cause": """In COBOL execution:
- **File Status 35 (File Not Found)**:
  1. The dataset specified on the JCL DD card does not exist in the z/OS catalog.
  2. The file is defined as `SELECT ... ASSIGN TO CUSTDD` but no `//CUSTDD DD` card was provided in the JCL step.
  3. In CICS, the file is defined in the CSD with a DSNAME that was deleted or renamed.""",
        "solution": """### 1. Verify Dataset Existence via IDCAMS LISTCAT
In ISPF or via batch JCL:
```jcl
//STEP1    EXEC PGM=IDCAMS
//SYSPRINT DD SYSOUT=*
//SYSIN    DD *
  LISTCAT ENT('PROD.KSDS.CUSTOMER')
/*
```
If output returns `IDC3012I ENTRY NOT FOUND`, the dataset was purged or un-cataloged.

### 2. Handle Optional Datasets in COBOL Syntax
If a file may or may not exist on any given run, declare it as `OPTIONAL`:
```cobol
       SELECT OPTIONAL CUSTVSAM
           ASSIGN TO CUSTDD
           ORGANIZATION IS INDEXED
           ACCESS MODE IS RANDOM
           RECORD KEY IS CUST-KEY
           FILE STATUS IS WS-CUST-STATUS.
```
When an `OPTIONAL` file does not exist:
- `OPEN INPUT` succeeds with `FILE STATUS = '05'` instead of crashing with `35`!
- The first `READ` returns `AT END` (`FILE STATUS = '10'`).

### 3. Verify CICS File Resource Definition
In CICS:
```text
CEMT INQUIRE FILE(CUSTFIL)
```
If `STATUS: UNENABLED`, check `DSNAME`. Re-point to the correct physical dataset using `CEDA ALTER FILE(CUSTFIL) DSNAME(...)` and reinstall.""",
        "prevention": [
            "Use `SELECT OPTIONAL` for conditional batch reconciliation and delta files.",
            "Verify automated dataset creation steps execute prior to dependent consumer steps.",
            "Check user catalog aliases (`IDCAMS DEFINE ALIAS`) to ensure HLQs route to correct catalogs."
        ],
        "references": [
            {"title": "IBM Enterprise COBOL: File Status Key Values", "url": "https://www.ibm.com/docs/en/cobol-zos/latest?topic=processing-file-status-key"},
            {"title": "IBM DFSMS Access Method Services for Catalogs", "url": "https://www.ibm.com/docs/en/zos/latest?topic=catalogs-managing-catalog-entries"}
        ]
    },
    {
        "slug": "vsam-alternate-index-aix-upgrade-degradation",
        "title": "Tuning VSAM Alternate Index (AIX) Performance: Managing UPGRADE Sets and BLDINDEX Latency",
        "date": "2026-09-27",
        "category": "CICS & VSAM Architecture",
        "tags": ["VSAM", "AIX", "Alternate Index", "BLDINDEX", "UPGRADE Set", "Performance"],
        "reading_time": "10 min read",
        "tldr": "VSAM Alternate Indexes (AIX) enable record access by secondary keys (such as SSN or Phone Number), but un-tuned UPGRADE sets can degrade batch insert performance by 500%. Discover how to manage UPGRADE sets and execute high-speed BLDINDEX batch rebuilds.",
        "problem": """A batch program that loads 2 million records into a customer VSAM KSDS takes 15 minutes when loading the base cluster alone, but balloons to over 3.5 hours when the Alternate Index (AIX) is attached to the upgrade set.""",
        "root_cause": """A VSAM Alternate Index is a separate KSDS that points to primary keys in the base cluster:
- When defined with `UPGRADE` attribute, every single `WRITE`, `REWRITE`, or `DELETE` against the base cluster immediately forces VSAM to execute synchronous I/O to update the AIX index and data components.
- During bulk data loads, maintaining active upgrade sets creates massive head contention and I/O bottlenecks.""",
        "solution": """### 1. Drop AIX from Upgrade Set During Bulk Batch Loads
Before executing high-volume bulk loads, remove the AIX from the upgrade set:
```jcl
//STEP1    EXEC PGM=IDCAMS
//SYSPRINT DD SYSOUT=*
//SYSIN    DD *
  ALTER PROD.KSDS.CUSTOMER.AIX NOUPGRADE
/*
```

### 2. Execute Fast Bulk Load into Base Cluster
Load the base cluster at maximum sequential speed using `REPRO` or optimized batch COBOL.

### 3. Rebuild the Alternate Index using High-Speed BLDINDEX
Rebuild the AIX in a single optimized pass using IDCAMS `BLDINDEX`:
```jcl
//BLDSTEP  EXEC PGM=IDCAMS
//SYSPRINT DD SYSOUT=*
//SYSIN    DD *
  BLDINDEX INFILE(BASEDD) -
           OUTFILE(AIXDD) -
           SORTKEYS
/*
//BASEDD   DD DSN=PROD.KSDS.CUSTOMER,DISP=SHR
//AIXDD    DD DSN=PROD.KSDS.CUSTOMER.AIX,DISP=SHR
```

### 4. Re-attach to Upgrade Set for Online CICS Access
Once rebuild is complete, restore the upgrade attribute for online transactions:
```jcl
//STEP3    EXEC PGM=IDCAMS
//SYSIN    DD *
  ALTER PROD.KSDS.CUSTOMER.AIX UPGRADE
/*
```""",
        "prevention": [
            "Always use `NOUPGRADE` and `BLDINDEX` for bulk data loads exceeding 50,000 records.",
            "Allocate adequate `SORTWKnn` datasets for `BLDINDEX` to perform in-memory sorting.",
            "Define Path components (`DEFINE PATH`) with `NOUPDATE` for read-only reporting jobs."
        ],
        "references": [
            {"title": "IBM DFSMS Access Method Services: BLDINDEX Command", "url": "https://www.ibm.com/docs/en/zos/latest?topic=commands-bldindex"},
            {"title": "IBM Redbooks: VSAM Demystified (SG24-6105)", "url": "https://www.redbooks.ibm.com/abstracts/sg246105.html"}
        ]
    },
    {
        "slug": "ims-status-code-ai-open-error-troubleshooting",
        "title": "Diagnosing IMS DL/I Status Code 'AI': Resolving Database Open Failures and Missing DD Cards",
        "date": "2026-09-27",
        "category": "CICS & VSAM Architecture",
        "tags": ["IMS DB", "DL/I", "Status Code AI", "Database Open", "PSB", "DBD"],
        "reading_time": "9 min read",
        "tldr": "IMS DL/I status code 'AI' signals an open error on a physical database dataset. Learn how to diagnose missing DD statements, data set authorization failures, and dynamic allocation (DFSMDA) mismatches.",
        "problem": """An IMS batch message processing (BMP) job or DL/I batch program terminates on its first database call:
```text
CBLTDLI CALL FAILED: FUNCTION 'GU  '
PCB STATUS CODE = 'AI'
CEE3250C The system or user abend U0456 was issued.
```
The program is unable to access customer master records, halting the cycle.""",
        "root_cause": """In IBM IMS Database Manager:
- **Status Code 'AI' (Open Error)** indicates DL/I was unable to open the physical OSAM or VSAM dataset associated with the target database:
  1. The JCL is missing the DD statement corresponding to the `DATASET DD1=` parameter in the DBD.
  2. If using IMS Dynamic Allocation, the `DFSMDA` macro member is missing from `IMS.RESLIB` or `DFSRESLB`.
  3. The dataset was migrated to tape by HSM or is locked by another job with `DISP=OLD`.""",
        "solution": """### 1. Identify the Missing DD Name from the DBD
Inspect the Database Definition (DBD) source for the target database:
```text
DBD  NAME=CUSTDBD,ACCESS=(HDAM,VSAM)
DATASET DD1=CUSTDAT1,DEVICE=3390
```
The required DD statement name is `CUSTDAT1`.

### 2. Verify JCL DD Allocation
Ensure your execution JCL includes the DD card:
```jcl
//CUSTDAT1 DD DSN=PROD.IMS.CUSTDBD.DATA,DISP=SHR
```

### 3. Verify Dynamic Allocation (DFSMDA)
If using Dynamic Allocation (recommended for production):
```jcl
//ASMSTEP  EXEC PGM=ASMA90
//SYSIN    DD *
  DFSMDA TYPE=INITIAL
  DFSMDA TYPE=DATASET,DSNAME=PROD.IMS.CUSTDBD.DATA,DDNAME=CUSTDAT1
  DFSMDA TYPE=FINAL
  END
/*
```
Ensure the assembled member `CUSTDAT1` is linked into `IMS.MDALIB` and concatenated in the execution `IMS` DD.""",
        "prevention": [
            "Use IMS Dynamic Allocation (`DFSMDA`) exclusively to avoid maintaining manual DD statements in hundreds of JCL jobs.",
            "Verify datasets are recalled from HSM (`HRECALL`) prior to launching scheduled batch streams.",
            "Check RACF dataset authorizations for the IMS control region user ID."
        ],
        "references": [
            {"title": "IBM IMS Messages and Codes: DL/I Status Codes", "url": "https://www.ibm.com/docs/en/ims/latest?topic=codes-dli-status"},
            {"title": "IBM IMS System Definition: DFSMDA Macro", "url": "https://www.ibm.com/docs/en/ims/latest?topic=macros-dfsmda"}
        ]
    },
    {
        "slug": "ims-status-code-ge-segment-not-found",
        "title": "Handling IMS DL/I Status Code 'GE': Navigating Unmatched Key Ranges and Boolean SSAs",
        "date": "2026-09-27",
        "category": "CICS & VSAM Architecture",
        "tags": ["IMS DB", "DL/I", "Status Code GE", "SSA", "Segment Not Found", "COBOL"],
        "reading_time": "8 min read",
        "tldr": "IMS DL/I status code 'GE' indicates the requested segment was not found (equivalent to SQLCODE +100). Learn how to handle 'GE' gracefully, optimize qualified Segment Search Arguments (SSAs), and navigate hierarchical paths.",
        "problem": """A COBOL IMS transaction looking up an account number abends with U4038 because the developer treats status code 'GE' as an unhandled system failure rather than a standard 'record not found' business condition.""",
        "root_cause": """When issuing DL/I calls (`GU`, `GHU`, `GN`):
- A blank status code (`'  '`) indicates success.
- **Status Code 'GE'** indicates DL/I searched the database according to the supplied Segment Search Argument (SSA) but found no segment meeting the qualification criteria.
- In parent-child relationships, 'GE' is also returned when reading past the last child segment under a parent.""",
        "solution": """### 1. Construct Qualified SSA in Working-Storage
```cobol
       01  ACCOUNT-SSA.
           05  FILLER           PIC X(08) VALUE 'ROOTSEG '.
           05  FILLER           PIC X(01) VALUE '('.
           05  FIELD-NAME       PIC X(08) VALUE 'ACCTNO  '.
           05  OPERATOR         PIC X(02) VALUE '= '.
           05  KEY-VALUE        PIC X(10) VALUE 'ACC90214  '.
           05  FILLER           PIC X(01) VALUE ')'.
```

### 2. Handle 'GE' Gracefully in COBOL Logic
```cobol
       CALL 'CBLTDLI' USING GU
                            CUST-PCB
                            CUST-IO-AREA
                            ACCOUNT-SSA.

       EVALUATE PCB-STATUS-CODE
           WHEN '  '
               PERFORM 2000-PROCESS-ACCOUNT
           WHEN 'GE'
      * Record does not exist - business condition
               MOVE 'Account Not Found' TO WS-ERROR-MSG
               PERFORM 3000-NOT-FOUND-ROUTINE
           WHEN OTHER
      * True technical failure
               PERFORM 9999-HANDLE-IMS-ABEND
       END-EVALUATE.
```""",
        "prevention": [
            "Never terminate programs abruptly when status code is 'GE'.",
            "Verify key padding (ensure search keys match the exact field length defined in the DBD).",
            "Use Boolean SSAs (`*` for AND, `+` for OR) carefully to avoid full database scans."
        ],
        "references": [
            {"title": "IBM IMS Application Programming: DL/I Calls and Status Codes", "url": "https://www.ibm.com/docs/en/ims/latest?topic=calls-dli-status-codes"},
            {"title": "StackMF Mainframe Core Engineering Pods", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },
    {
        "slug": "telon-batch-driver-to-cobol-modernization",
        "title": "Migrating CA-Telon Batch Drivers and TDF Panels into Modular Enterprise COBOL 6.x",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["Telon", "CA-Telon", "COBOL", "Modernisation", "Broadcom Replacement", "TDF"],
        "reading_time": "11 min read",
        "tldr": "Eliminate proprietary Broadcom CA-Telon batch drivers and generated spaghetti code. Discover how to extract business logic from Telon Development Facility (TDF) tables, eliminate the TLNMAIN driver, and refactor into clean, modern COBOL 6.x.",
        "problem": """Enterprises trapped in CA-Telon spend millions in support fees for an obsolete 4GL tool. Batch reporting programs generated by Telon contain obfuscated driver loops that prevent optimization and block migration to modern DevOps CI/CD.""",
        "root_cause": """CA-Telon batch programs do not contain clean standard `PROCEDURE DIVISION` logic:
- Execution is driven by the proprietary Telon batch driver module (`TLNMAIN`).
- Program logic is split into generated paragraphs (`PG100`, `PG200`) interspersed with proprietary Telon internal flags (`TLN-EOF`, `TLN-ERR`).
- Compiling requires proprietary Telon macro libraries and pre-compilers.""",
        "solution": """### 1. Reverse-Engineer the Telon Execution Loop
Examine the Telon driver structure:
```text
TLNMAIN -> Initializes Telon buffers -> Calls generated module
        -> Handles I/O via Telon Access Modules -> Loops until TLN-DONE
```

### 2. Extract Business Logic into Pure Native COBOL
Extract validation rules and calculation logic from custom Telon exit sections (`CUSTOM SECTION` / `MOD-SECT`), eliminating all `TLN*` prefixes:
```cobol
       IDENTIFICATION DIVISION.
       PROGRAM-ID. BILLING01.
       ENVIRONMENT DIVISION.
       INPUT-OUTPUT SECTION.
       FILE-CONTROL.
           SELECT BILL-FILE ASSIGN TO BILLDD
                  ORGANIZATION IS SEQUENTIAL
                  FILE STATUS IS WS-BILL-STATUS.

       PROCEDURE DIVISION.
       0000-MAIN.
           OPEN INPUT BILL-FILE
           PERFORM UNTIL WS-BILL-STATUS = '10'
               READ BILL-FILE
                   AT END MOVE '10' TO WS-BILL-STATUS
                   NOT AT END PERFORM 1000-PROCESS-RECORD
               END-READ
           END-PERFORM
           CLOSE BILL-FILE
           GOBACK.
```

### 3. Recompile with Enterprise COBOL 6.4
Compile using modern IBM compiler flags (`OPT(2),ARCH(14)`), completely eliminating Broadcom Telon license dependencies!""",
        "prevention": [
            "De-license CA-Telon runtime modules from all test and production load libraries.",
            "Establish automated unit tests verifying input/output parity during refactoring.",
            "Partner with StackMF's modernization pods for automated Telon extraction tooling."
        ],
        "references": [
            {"title": "Broadcom CA Telon Decommissioning Best Practices", "url": "https://support.broadcom.com"},
            {"title": "StackMF Broadcom Product Replacement Program", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },
    {
        "slug": "ca7-dataset-trigger-missed-event-resolution",
        "title": "Fixing CA-7 Data Set Trigger (DSN) Failures: Resolving Missed SMF Type 15 Close Events",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["CA-7", "Workload Automation", "Dataset Triggers", "SMF", "Broadcom Replacement"],
        "reading_time": "10 min read",
        "tldr": "CA-7 Data Set Triggers (DSN) automatically initiate downstream batch jobs when an input file is closed. Troubleshoot why jobs fail to trigger due to disposition issues (DISP=MOD vs NEW), SMF Type 15 intercept drops, or SASSSMI0 exits.",
        "problem": """A critical overnight billing job fails to launch automatically in CA-7 after upstream step `STEP040` finishes writing `PROD.FEED.DAILY`. Operations teams wait hours before discovering the schedule stalled.""",
        "root_cause": """CA-7 monitors dataset creation using the SMF Type 14/15 close exit (`SASSSMI0`):
1. **Disposition Filtering**: CA-7 only triggers on datasets closed successfully with `DISP=(NEW,CATLG)` or `DISP=(MOD,CATLG)` if configured in the dataset definition.
2. **Step Condition Code**: If the creating step abended or completed with a condition code higher than the threshold, CA-7 suppresses the trigger.
3. **Queue Full / Exit Deactivated**: If the CA-7 SMF intercept queue fills up during peak traffic, SMF records drop.""",
        "solution": """### 1. Inquire Dataset Definition in CA-7
From the CA-7 3270 terminal:
```text
LDSN,DSN=PROD.FEED.DAILY
```
Verify attributes:
- `TRIG`: Ensure dataset trigger is enabled (`YES`).
- `RO`: Check reverse offset and creation criteria.

### 2. Check the Creating Step JCL Disposition
Ensure the dataset was created with a triggering disposition:
```jcl
//SYSUT2   DD DSN=PROD.FEED.DAILY,
//            DISP=(NEW,CATLG,DELETE),
//            SPACE=(CYL,(50,10)),UNIT=SYSDA
```
If using `DISP=SHR`, CA-7 will NOT trigger unless `TRIGGER=ALWAYS` is explicitly configured.

### 3. Manually Demand the Successor Job
To restore production while diagnosing:
```text
DEMAND,JOB=BILLNIGHT,SET=ND
```""",
        "prevention": [
            "Verify SMF intercept exit `SASSSMI0` status during system IPLs.",
            "Avoid relying on `DISP=MOD` for dataset triggers; standardize on `DISP=(NEW,CATLG)`.",
            "Migrate from CA-7 to Stonebranch Universal Automation Center (UAC) for robust event-driven webhook triggers."
        ],
        "references": [
            {"title": "Broadcom CA 7 Workload Automation Documentation", "url": "https://techdocs.broadcom.com"},
            {"title": "StackMF CA-7 to Stonebranch Replacement", "url": "https://stackmf.com/#tco-calculator"}
        ]
    },
    {
        "slug": "ca7-late-and-unstarted-job-troubleshooting",
        "title": "Resolving CA-7 LATE and LJOB Delays: Diagnosing Predecessor Hold Dependencies and Resource Depth",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["CA-7", "LATE", "Workload Automation", "Queue Management", "Troubleshooting"],
        "reading_time": "10 min read",
        "tldr": "When critical batch jobs are flagged as LATE in CA-7, immediate action is required to avoid breaching SLAs. Learn how to parse CA-7 Queue displays (LQ, LJOB), inspect Virtual Resource Management (VRM) locks, and release predecessor holds.",
        "problem": """The CA-7 operations console flashes continuous alerts:
```text
CA-7.001 - JOB ACCNT01 IS LATE FOR START AT 03:00:00 ON 2026.270
CA-7.002 - SLA DEADLINE BREACH IMMINENT FOR FLOW 'GLOBAL_CLEARING'
```
The job remains in the Request Queue (`REQ`), refusing to submit to the z/OS JES2 queue.""",
        "root_cause": """Jobs in the CA-7 Request Queue are evaluated against three gates:
1. **Predecessor Requirements**: Has every predecessor job completed with acceptable condition codes?
2. **Dataset Dependencies**: Are required input datasets cataloged and closed?
3. **Virtual Resource Management (VRM)**: Are required exclusive resources (e.g. database locks, tape drives) currently held by another job?""",
        "solution": """### 1. Inquire Why the Job is Waiting
Issue the detailed status query in CA-7:
```text
LJOB,JOB=ACCNT01,LIST=ALL
```
Look at the `REQUIREMENTS` section:
```text
PRED-JOB: FEEDJOB1 - NOT SATISFIED (WAITING)
VRM-RES : DB2_TABLE_LOCK - HELD EXCLUSIVELY BY JOBPAY02
```

### 2. Satisfy or Override Predecessor Requirements
If predecessor `FEEDJOB1` completed outside CA-7 or was verified manually:
```text
POST,JOB=ACCNT01,DEPJOB=FEEDJOB1
```

### 3. Release Virtual Resource Contention
Check who holds the VRM resource:
```text
LQ,ST=RES,RES=DB2_TABLE_LOCK
```
Once `JOBPAY02` completes, CA-7 immediately releases the resource and submits `ACCNT01` to JES2!""",
        "prevention": [
            "Regularly audit CA-7 base calendars to ensure holiday schedules don't block predecessors.",
            "Use Virtual Resource depths appropriately rather than exclusive locks where shared access is safe.",
            "Engage StackMF to automate CA-7 migration to modern hybrid schedulers (Control-M, Stonebranch)."
        ],
        "references": [
            {"title": "Broadcom CA 7 Commands Reference", "url": "https://techdocs.broadcom.com"},
            {"title": "StackMF Broadcom Savings Calculator", "url": "https://stackmf.com/#tco-calculator"}
        ]
    },
    {
        "slug": "endevor-signout-lock-package-cast-failure",
        "title": "Clearing Orphaned Endevor Signout Locks and Resolving Package Cast Return Code 12",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["Endevor", "Broadcom", "Signout Lock", "Package Cast", "DevOps"],
        "reading_time": "9 min read",
        "tldr": "Broadcom Endevor package cast failures (RC=12) occur when elements are signed out to other users or locked by concurrent change control. Learn how to inspect element master records, clear orphaned signouts, and cast packages cleanly.",
        "problem": """A release engineer attempts to Cast an Endevor package for a midnight emergency release:
```text
C1G0204E ELEMENT MODPAY01 IN STAGE 1 IS SIGNED OUT TO USER 'DEVELOPER1'
C1G0255E PACKAGE CAST FAILED - RETURN CODE = 12
```
The engineer who locked the element is on leave, blocking the entire production deployment.""",
        "root_cause": """Broadcom Endevor uses signout locks (`SIGNOUT=Y`):
- When an engineer retrieves or edits an element, Endevor writes their User ID to the Master Control File (MCF).
- Only the signout owner or an Endevor administrator with `SIGNOUT OVERRIDE` authority can cast or promote packages containing that element.""",
        "solution": """### 1. View Element Signout Status in ISPF
In Endevor:
1. Select Option `2` (Display) &rarr; Option `1` (Element).
2. Enter Environment, System, Subsystem, and Element Name (`MODPAY01`).
3. Note the `SIGNOUT USER ID`.

### 2. Override Signout Lock via Endevor Batch SCL
Execute an authorized SCL batch job with `OVERRIDE SIGNOUT`:
```jcl
//ENDEVOR  EXEC PGM=NDVRC1,PARM='C1BM3000'
//SYSPRINT DD SYSOUT=*
//BSTIPT   DD *
  SIGNIN ELEMENT MODPAY01
    FROM ENVIRONMENT 'DEV'
         SYSTEM 'BILLING'
         SUBSYSTEM 'CORE'
         TYPE 'COBOL'
         STAGE 1
    OVERRIDE SIGNOUT.
/*
```

### 3. Re-Cast the Endevor Package
Once the lock is released:
```text
CAST PACKAGE 'PKG20260927A'
```
The package casts with `RETURN CODE = 00` and proceeds to approval!""",
        "prevention": [
            "Establish automated signin cleanup jobs for inactive developer IDs.",
            "Migrate from Endevor's proprietary lock model to Git's modern branch-and-merge workflow.",
            "Leverage StackMF's turnkey Endevor-to-Git migration accelerator to eliminate lockouts forever."
        ],
        "references": [
            {"title": "Broadcom Endevor Software Change Manager Documentation", "url": "https://techdocs.broadcom.com"},
            {"title": "StackMF Broadcom Endevor Replacement", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },
    {
        "slug": "changeman-zmf-component-recompile-drift",
        "title": "Preventing ChangeMan ZMF Component Desynchronization with Automated Cross-Reference (XREF)",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["ChangeMan", "ChangeMan ZMF", "XREF", "Desynchronization", "DevOps"],
        "reading_time": "9 min read",
        "tldr": "In Serena / Micro Focus ChangeMan ZMF, modifying a shared copybook without recompiling all dependent COBOL programs creates silent runtime data corruption. Discover how to configure ChangeMan XREF data collection and audit triggers.",
        "problem": """A developer updates copybook `CUSTREC.CPY` to expand a zip code field from 5 to 9 digits in ChangeMan package `CHG001`. Program A is staged and recompiled, but Program B (which also uses `CUSTREC`) is forgotten. At runtime, Program B corrupts adjacent memory, causing production ABEND S0C7.""",
        "root_cause": """Static copybook references are baked into compiled load modules at compile time.
If an enterprise SCM does not automatically cross-reference dependencies:
- Modifying a copybook invalidates all load modules compiled with the older version.
- **ChangeMan XREF (Cross-Reference)** maintains a database of copybook-to-program relationships and warns release managers during package audit if dependent modules were not staged.""",
        "solution": """### 1. Query ChangeMan XREF for Dependent Components
In ISPF ChangeMan ZMF:
1. Navigate to Option `X` (XREF).
2. Select **Component-to-Program Cross Reference**.
3. Enter Copybook Name: `CUSTREC`.
ChangeMan lists all 14 COBOL programs that include this copybook!

### 2. Stage All Dependent Programs into the Package
Stage all 14 programs into `CHG001` so they recompile with the new copybook layout:
```text
STAGE PROGRAM(MODB01) PACKAGE(CHG001)
STAGE PROGRAM(MODB02) PACKAGE(CHG001)
```

### 3. Run Automated Package Audit
Run Audit (Option `1.A`). If any dependent program is omitted, Audit returns `RC=08`, blocking promotion until all affected programs are recompiled.""",
        "prevention": [
            "Enable mandatory XREF validation in ChangeMan application administration settings.",
            "Run daily batch XREF rebuild jobs to keep dependency indices updated.",
            "Consider migrating to IBM Dependency Based Build (DBB) and Git for automated impact analysis."
        ],
        "references": [
            {"title": "Micro Focus ChangeMan ZMF Administrator Guide", "url": "https://www.microfocus.com"},
            {"title": "StackMF Modernization Practice", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },
    {
        "slug": "rexx-stem-variable-memory-leak-cleanup",
        "title": "Preventing Memory Leaks and TSO/E Exhaustion in High-Volume Enterprise REXX Automation",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["REXX", "Memory Leak", "Stem Variables", "DROP", "TSO/E", "Performance"],
        "reading_time": "9 min read",
        "tldr": "REXX stem variables (e.g. RECORD.i) allocate virtual memory dynamically. In long-running automation loops processing millions of records, failing to drop stems causes virtual storage exhaustion and TSO/E ABEND S878. Learn memory management best practices in REXX.",
        "problem": """An automated REXX script parsing syslog or SMF records runs for 2 hours and crashes with:
```text
IRX0250E User storage capacity exceeded.
SYSTEM COMPLETION CODE=878  REASON CODE=00000010
Error running SYSLOGP, line 142: Out of memory.
```
The monitoring automation dies, blinding operations teams.""",
        "root_cause": """REXX manages variable memory in the Language Environment / TSO heap:
- Every stem assignment (`LINE.i = record`) creates a new symbol table entry and allocates memory buffers.
- Setting `LINE.0 = 0` only resets the count variable; it **does NOT free** the memory buffers held by `LINE.1` through `LINE.100000`!
- Over iterations, memory accumulates until 24-bit/31-bit storage is exhausted.""",
        "solution": """### 1. Use the REXX DROP Statement to Free Memory
Always explicitly drop stem variables when a processing batch finishes:
```rexx
/* Process chunk of records */
Do i = 1 To line_count
  /* Process LINE.i */
End

/* CORRECT: Frees all allocated memory in the stem */
Drop LINE.
```

### 2. Process Records in Bounded Batches
Avoid reading 2 million lines into memory at once. Process in chunks:
```rexx
/* Bounded chunk processing */
Do While Lines(input_file) > 0
  chunk_count = 0
  Do While Lines(input_file) > 0 & chunk_count < 1000
    chunk_count = chunk_count + 1
    BUFFER.chunk_count = Linein(input_file)
  End

  /* Process the 1000 lines */
  Call Process_Batch chunk_count

  /* Release memory */
  Drop BUFFER.
End
```

### 3. Clear Subroutines with PROCEDURE EXPOSE
Limit variable scope in functions:
```rexx
Process_Record: Procedure Expose shared_config.
  /* Local variables are automatically freed upon RETURN */
  Parse Arg raw_line
  /* ... */
  Return 0
```""",
        "prevention": [
            "Always use `Drop STEM.` (with trailing period) to free stem memory arrays.",
            "Scope subroutines with `PROCEDURE` to avoid polluting the global variable dictionary.",
            "Monitor TSO region sizes in batch JCL (specify `REGION=64M` or higher for heavy scripting)."
        ],
        "references": [
            {"title": "IBM TSO/E REXX Reference: DROP Instruction", "url": "https://www.ibm.com/docs/en/zos/latest?topic=instructions-drop"},
            {"title": "StackMF Mainframe Core Engineering Services", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },
    {
        "slug": "rexx-parsing-smf-records-system-auditing",
        "title": "Parsing z/OS SMF Type 30 (Job Accounting) and Type 110 (CICS Telemetry) Records with REXX",
        "date": "2026-09-27",
        "category": "DevOps & Automation",
        "tags": ["REXX", "SMF", "Telemetry", "Auditing", "z/OS", "Automation"],
        "reading_time": "10 min read",
        "tldr": "System Management Facilities (SMF) records are the black box of z/OS. Discover how to write high-speed REXX scripts that decode SMF Type 30 (CPU/Job accounting) and Type 110 (CICS transaction metrics) without purchasing expensive third-party reporting tools.",
        "problem": """IT leadership demands daily reports showing top CPU-consuming batch jobs and CICS transaction counts, but licensing costs for third-party reporting tools (SAS, MICS, MXG) are prohibitive.""",
        "root_cause": """z/OS writes all execution metrics into raw binary SMF datasets:
- SMF records contain standard headers followed by self-defining sections (triplets: Offset, Length, Number of sections).
- Using REXX functions like `C2D` (Character to Decimal) and `C2X` (Character to Hex), binary SMF records can be decoded directly into human-readable CSV or JSON files.""",
        "solution": """### 1. Extract SMF Records via IFASMFDP
Dump Type 30 records to a sequential dataset:
```jcl
//SMFDUMP  EXEC PGM=IFASMFDP
//SYSPRINT DD SYSOUT=*
//DUMPIN   DD DSN=SYS1.MAN1,DISP=SHR
//DUMPOUT  DD DSN=&&SMF30,DISP=(NEW,PASS),SPACE=(CYL,(50,10))
//SYSIN    DD *
  INDD(DUMPIN,OPTIONS(DUMP))
  OUTDD(DUMPOUT,TYPE(30))
/*
```

### 2. Decode Binary Headers in REXX
```rexx
/* REXX - DECODE SMF TYPE 30 RECORD */
"EXECIO * DISKR SMFFILE (STEM REC. FINIS"

Do i = 1 To REC.0
  record = REC.i
  smf_len = C2D(Substr(record, 1, 2))
  smf_type = C2D(Substr(record, 6, 1))

  If smf_type = 30 Then Do
    /* Extract Job Name from Identification Section */
    job_name = Strip(Substr(record, 19, 8))
    user_id  = Strip(Substr(record, 27, 8))

    /* Extract CPU Time (Hundredths of a second) */
    cpu_offset = C2D(Substr(record, 41, 4))
    cpu_raw = Substr(record, cpu_offset + 1, 4)
    cpu_seconds = C2D(cpu_raw) / 100

    Say "Job: " job_name " User: " user_id " CPU: " cpu_seconds "s"
  End
End
Exit 0
```""",
        "prevention": [
            "Verify SMF triplet offsets dynamically rather than hardcoding record positions.",
            "Filter SMF records during `IFASMFDP` extraction to keep REXX input files manageable.",
            "Stream parsed SMF metrics into Elasticsearch or Grafana for modern cloud dashboarding."
        ],
        "references": [
            {"title": "IBM z/OS MVS System Management Facilities (SMF)", "url": "https://www.ibm.com/docs/en/zos/latest?topic=smf-system-management-facilities"},
            {"title": "StackMF Mainframe Modernization Practice", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },
    {
        "slug": "cobol-json-generate-json-parse-zowe-apis",
        "title": "Native JSON Parsing and Generation in Enterprise COBOL 6.x for Modern REST Gateways",
        "date": "2026-09-27",
        "category": "Modernisation & Cloud",
        "tags": ["COBOL 6.x", "JSON PARSE", "JSON GENERATE", "REST API", "Modernisation"],
        "reading_time": "10 min read",
        "tldr": "Eliminate middleware gateways. Discover how to use Enterprise COBOL 6.x native JSON GENERATE and JSON PARSE statements to consume and emit UTF-8 JSON payloads directly inside z/OS batch and CICS programs.",
        "problem": """A modern microservice sends JSON payloads to a mainframe banking service. Developers previously wrote hundreds of lines of brittle substring parsing code to extract customer values from the text string, causing production crashes whenever JSON key order varied.""",
        "root_cause": """JSON is hierarchical and variable-length, while COBOL relies on fixed-width structures.
In **Enterprise COBOL 6.2+**:
- The compiler includes native statements: `JSON PARSE` and `JSON GENERATE`.
- Automatically maps JSON objects and arrays into COBOL group items and `OCCURS` tables with full Unicode UTF-8 and EBCDIC conversion.""",
        "solution": """### 1. Define the COBOL Data Structure
```cobol
       01  CUSTOMER-PAYLOAD.
           05  ACCOUNT-ID       PIC X(10).
           05  CUSTOMER-NAME    PIC X(30).
           05  BALANCE          PIC S9(7)V99 COMP-3.
```

### 2. Parse Incoming JSON String into COBOL
```cobol
       JSON PARSE WS-JSON-INPUT INTO CUSTOMER-PAYLOAD
           WITH DETAIL
           NAME OF ACCOUNT-ID IS 'accountId'
                   CUSTOMER-NAME IS 'name'
                   BALANCE IS 'balance'
           ON EXCEPTION
               DISPLAY 'JSON Parse Failed! Code: ' XML-CODE
               PERFORM 9900-HANDLE-JSON-ERROR
           NOT ON EXCEPTION
               PERFORM 2000-PROCESS-DATA
       END-JSON.
```

### 3. Generate JSON Output from COBOL Structure
```cobol
       JSON GENERATE WS-JSON-OUTPUT FROM CUSTOMER-PAYLOAD
           NAME OF ACCOUNT-ID IS 'accountId'
                   CUSTOMER-NAME IS 'name'
                   BALANCE IS 'balance'
           COUNT IN WS-CHAR-COUNT
           ON EXCEPTION
               PERFORM 9900-HANDLE-GEN-ERROR
       END-JSON.
```
Result in `WS-JSON-OUTPUT`:
```json
{"accountId":"ACC-90214","name":"ACME CORP","balance":14250.75}
```""",
        "prevention": [
            "Specify `NAME OF` phrases to map camelCase JSON properties to hyphenated COBOL identifiers.",
            "Ensure the receiving JSON buffer (`WS-JSON-OUTPUT`) is sized generously to prevent truncation.",
            "Compile with `CODEPAGE(1140)` or `(1047)` to handle international currency symbols."
        ],
        "references": [
            {"title": "IBM Enterprise COBOL for z/OS: JSON GENERATE Statement", "url": "https://www.ibm.com/docs/en/cobol-zos/latest?topic=statements-json-generate"},
            {"title": "IBM Enterprise COBOL for z/OS: JSON PARSE Statement", "url": "https://www.ibm.com/docs/en/cobol-zos/latest?topic=statements-json-parse"}
        ]
    },
    {
        "slug": "db2-multi-row-fetch-insert-batch-tuning",
        "title": "Accelerating Batch SQL by 400%: Implementing DB2 Multi-Row FETCH and Multi-Row INSERT in COBOL",
        "date": "2026-09-27",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "Multi-Row FETCH", "Multi-Row INSERT", "Performance", "COBOL DB2"],
        "reading_time": "10 min read",
        "tldr": "Single-row SQL cursors incur CPU cross-memory switching costs on every single row. Learn how to implement DB2 for z/OS Multi-Row FETCH and Multi-Row INSERT in COBOL, reducing batch elapsed times and CPU consumption by up to 70%.",
        "problem": """An overnight batch billing program takes 3 hours to process 10 million DB2 rows. The developer discovers that 80% of the CPU time is burned in DB2 cross-memory context switches executing `FETCH` 10 million individual times.""",
        "root_cause": """Every `EXEC SQL FETCH` or `INSERT` statement incurs:
- Address space cross-memory switching between application and DB2 Data Manager (DSNDB01).
- SQL validation and lock acquisition overhead.
**Multi-Row Operations (MRF / MRI)**:
- Transports arrays of 100 to 1,000 rows across the address space boundary in a **single CPU call**, slashing context switching by 99%!""",
        "solution": """### 1. Declare Cursor for Multi-Row FETCH
In COBOL Working-Storage:
```cobol
       01  WS-ROW-ARRAYS.
           05  WS-ACCT-ID       OCCURS 100 TIMES PIC X(10).
           05  WS-BALANCE       OCCURS 100 TIMES PIC S9(7)V99 COMP-3.
       01  WS-ROWS-FETCHED      PIC S9(9) COMP.

       EXEC SQL
           DECLARE CUST_CSR CURSOR FOR
           SELECT ACCT_ID, BALANCE
           FROM CUSTOMER
           FOR FETCH ONLY
       END-EXEC.
```

### 2. Execute Multi-Row FETCH Statement
```cobol
       EXEC SQL OPEN CUST_CSR END-EXEC.

       PERFORM UNTIL SQLCODE = 100
           EXEC SQL
               FETCH NEXT ROWSET 100 ROWS FROM CUST_CSR
               INTO :WS-ACCT-ID, :WS-BALANCE
           END-EXEC

           IF SQLCODE = 0 OR SQLCODE = 100
               PERFORM 2000-PROCESS-ROWSET
           END-IF
       END-PERFORM.
```

### 3. Multi-Row INSERT Syntax
Bulk insert 100 rows in a single SQL statement:
```cobol
       EXEC SQL
           INSERT INTO AUDIT_LOG (ACCT_ID, BALANCE)
           VALUES (:WS-ACCT-ID, :WS-BALANCE)
           FOR 100 ROWS
       END-EXEC.
```""",
        "prevention": [
            "Use rowset sizes between 50 and 500 for optimal memory-to-throughput balance.",
            "Inspect `SQLERRD(3)` in the SQLCA to determine the exact number of rows retrieved on partial final rowsets.",
            "Always specify `FOR FETCH ONLY` to allow DB2 block fetching."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS SQL Reference: Multi-Row FETCH", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=statements-fetch"},
            {"title": "IBM Db2 13 Performance Tuning: Multi-Row Operations", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=performance-multi-row-operations"}
        ]
    },
    {
        "slug": "syncsort-dfsort-icetool-batch-reporting",
        "title": "Replacing Custom COBOL Extract Programs with High-Performance DFSORT / ICETOOL Control Statements",
        "date": "2026-09-27",
        "category": "ABENDS & Diagnostics",
        "tags": ["DFSORT", "ICETOOL", "Batch", "Performance", "SyncSort", "Automation"],
        "reading_time": "9 min read",
        "tldr": "Writing full COBOL programs just to filter, reformat, and aggregate sequential files burns developer hours and CPU cycles. Learn how to use DFSORT and ICETOOL operators (SPLICE, SELECT, STATS, DISPLAY) to execute high-speed batch data manipulations directly in JCL.",
        "problem": """Developers write and compile custom 500-line COBOL programs just to filter active customer accounts from a sequential file and sum their balances, cluttering load libraries and taking weeks to promote through change control.""",
        "root_cause": """IBM DFSORT and ICETOOL are hardware-accelerated, zIIP-eligible utilities optimized for sorting, filtering, and reporting at near-channel speeds without compiling new programs.""",
        "solution": """### 1. Filter, Reformat, and Slice Fields with DFSORT
Extract records where `STATUS = 'ACT'` (Columns 1-3) and output only Account (Cols 10-19) and Balance (Cols 30-37):
```jcl
//SORTSTEP EXEC PGM=SORT
//SYSOUT   DD SYSOUT=*
//SORTIN   DD DSN=PROD.CUSTOMER.MASTER,DISP=SHR
//SORTOUT  DD DSN=PROD.CUSTOMER.EXTRACT,DISP=(NEW,CATLG,DELETE),
//            SPACE=(CYL,(10,5),RLSE)
//SYSIN    DD *
  INCLUDE COND=(1,3,CH,EQ,C'ACT')
  SORT FIELDS=(10,10,CH,A)
  OUTREC FIELDS=(10,10,30,8)
/*
```

### 2. Generate Statistical Reports with ICETOOL
Calculate Minimum, Maximum, and Average balance without writing a line of COBOL:
```jcl
//TOOLSTEP EXEC PGM=ICETOOL
//TOOLMSG  DD SYSOUT=*
//DFSMSG   DD SYSOUT=*
//INFILE   DD DSN=PROD.CUSTOMER.EXTRACT,DISP=SHR
//PRINTDD  DD SYSOUT=*
//TOOLIN   DD *
  STATS FROM(INFILE) ON(11,8,PD)
  DISPLAY FROM(INFILE) LIST(PRINTDD) -
          TITLE('MONTHLY ACCOUNT SUMMARY') -
          HEADER('ACCOUNT') ON(1,10,CH) -
          HEADER('BALANCE') ON(11,8,PD)
/*
```""",
        "prevention": [
            "Use ICETOOL for reporting and filtering before commissioning custom COBOL programs.",
            "Use `SPLICE` operator to perform high-speed two-file matches without database lookups.",
            "Ensure DFSORT is enabled for IBM z16 Sort Acceleration hardware."
        ],
        "references": [
            {"title": "IBM DFSORT Application Programming Guide (SC23-6878)", "url": "https://www.ibm.com/docs/en/zos/latest?topic=dfsort-application-programming"},
            {"title": "StackMF Mainframe Application Maintenance", "url": "https://stackmf.com/#maintenance-ams"}
        ]
    },
    {
        "slug": "cics-channels-containers-replacing-commarea",
        "title": "Breaking the 32KB Limit: Transitioning CICS Commareas to Channels and Containers",
        "date": "2026-09-27",
        "category": "CICS & VSAM Architecture",
        "tags": ["CICS TS", "Channels", "Containers", "Commarea", "Modernisation", "COBOL"],
        "reading_time": "10 min read",
        "tldr": "Traditional CICS communication is restricted by the rigid 32KB DFHCOMMAREA barrier. Discover how to modernize program-to-program and web interfaces using CICS Channels and Containers, supporting multi-megabyte JSON payloads and modular data structures.",
        "problem": """An enterprise extending a core CICS transaction to support modern web payloads hits the fatal architectural wall: `DFHCOMMAREA` exceeds 32,767 bytes, causing compiler error `IGYDS1089-E RECORD SIZE EXCEEDS MAXIMUM` and CICS ABEND `LENG`.""",
        "root_cause": """`DFHCOMMAREA` is addressed by a 16-bit halfword length field in the CICS Task Control Block (EIB), fundamentally capping memory transfer at 32KB.
**CICS Channels and Containers**:
- A **Channel** acts as a named collection of independent data payloads.
- Each **Container** holds arbitrary binary, character, or JSON data of unlimited size (gigabytes if needed!).
- Eliminates 32KB limitations and enables self-describing, named interfaces.""",
        "solution": """### 1. Put Data into a CICS Container
In the calling program:
```cobol
       01  WS-PAYLOAD-DATA      PIC X(100000).

       EXEC CICS PUT CONTAINER('CUSTOMER-REQUEST')
                 CHANNEL('BANKING-CHANNEL')
                 FROM(WS-PAYLOAD-DATA)
                 FLENGTH(LENGTH OF WS-PAYLOAD-DATA)
                 DATATYPE(DFHVALUE(CHAR))
       END-EXEC.

       EXEC CICS LINK PROGRAM('PROG02')
                 CHANNEL('BANKING-CHANNEL')
       END-EXEC.
```

### 2. Retrieve Data in the Called Program
In `PROG02`:
```cobol
       EXEC CICS GET CONTAINER('CUSTOMER-REQUEST')
                 INTO(WS-INPUT-BUFFER)
                 FLENGTH(WS-BUFFER-LEN)
       END-EXEC.

      * Process data and return response container
       EXEC CICS PUT CONTAINER('CUSTOMER-RESPONSE')
                 FROM(WS-RESPONSE-BUFFER)
                 FLENGTH(WS-RESP-LEN)
       END-EXEC.
```""",
        "prevention": [
            "Mandate Channels and Containers for all new CICS application developments.",
            "Use `DATATYPE(DFHVALUE(CHAR))` to allow CICS to automatically handle EBCDIC-to-UTF-8 codepage conversions.",
            "Delete unneeded containers via `EXEC CICS DELETE CONTAINER` to free 64-bit storage."
        ],
        "references": [
            {"title": "IBM CICS TS: Enhanced Program-to-Program Communication with Channels", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=programming-channels-containers"},
            {"title": "StackMF Modernization Bridge", "url": "https://stackmf.com/#fullstack-bridge"}
        ]
    },
    {
        "slug": "sub-capacity-reporting-tool-scrt-optimization",
        "title": "Decoding the SCRT Report: Identifying 4HRA Spikes and Sub-Capacity Pricing Anomalies",
        "date": "2026-09-27",
        "category": "DB2 SQL & Performance",
        "tags": ["SCRT", "4HRA", "MLC", "Cost Optimization", "WLM", "Capacity Planning"],
        "reading_time": "11 min read",
        "tldr": "IBM Monthly License Charges (MLC) are dictated by your monthly Sub-Capacity Reporting Tool (SCRT) submission. Learn how to parse SCRT CSV logs, identify which LPAR and batch workload caused the peak billing hour, and implement capacity caps.",
        "problem": """The enterprise CIO receives an unexpected 20% spike on the monthly IBM software invoice. Nobody on the mainframe team can identify which job or business event caused the peak billing hour to jump.""",
        "root_cause": """IBM bills software based on the highest simultaneous **Rolling 4-Hour Average (4HRA)** across the month:
- The SCRT tool scans SMF Type 70 (CPU activity) and Type 89 (product usage) records across all LPARs in the sysplex.
- It identifies the single peak hour where combined MSU consumption was highest.
- An unconstrained batch extraction job overlapping with online transaction processing during the peak window permanently sets the monthly software bill at a higher tier!""",
        "solution": """### 1. Execute and Generate the Monthly SCRT Report
```jcl
//SCRTSTEP EXEC PGM=ISRSCRT
//SYSPRINT DD SYSOUT=*
//SMFDATA  DD DSN=PROD.SMF.MONTHLY,DISP=SHR
//OUTPUT   DD DSN=PROD.SCRT.REPORT.CSV,DISP=(NEW,CATLG,DELETE),
//            SPACE=(CYL,(5,1))
```

### 2. Locate the Peak 4HRA Billing Hour in the Report
Open the generated CSV report. Search for section:
```text
Product Max / Peak Utilization:
Product: 5650-ZOS (z/OS V2)
Peak MSU: 1,420
Peak Date/Time: 2026-09-18 02:00:00 UTC
Contributing LPARs: LPAR1 (920 MSU), LPAR2 (500 MSU)
```
This isolates the exact date and hour of the spike: **September 18 at 02:00 UTC**.

### 3. Cross-Reference Peak Hour with SMF Type 30 Records
Query SMF Type 30 records between 00:00 and 04:00 UTC on September 18 to list jobs consuming the highest CPU:
```sql
SELECT JOBNAME, SUM(CPUTIME)
FROM SMF_TYPE30_TABLE
WHERE START_TIME BETWEEN '2026-09-18 00:00:00' AND '2026-09-18 04:00:00'
GROUP BY JOBNAME
ORDER BY 2 DESC;
```
Offending job identified: `UNLOAD_ALL_CUSTOMERS` ran concurrently with nightly database reorgs!

### 4. Implement WLM Defined Capacity and Schedule Staggering
1. Shift `UNLOAD_ALL_CUSTOMERS` to 04:30 AM (outside the 4HRA peak window).
2. In WLM, configure Defined Capacity on `LPAR1` to 850 MSUs, capping billing peaks automatically.""",
        "prevention": [
            "Audit SCRT reports weekly using predictive tools rather than waiting for the end of the month.",
            "Use WLM Group Capacity Limits across Parallel Sysplex LPARs.",
            "Recompile top CPU batch consumers with Enterprise COBOL `OPT(3)` to lower base MSU burn.",
            "Contact StackMF for our specialized Mainframe 4HRA Optimization Assessment."
        ],
        "references": [
            {"title": "IBM Sub-Capacity Reporting Tool User's Guide (SC23-6845)", "url": "https://www.ibm.com/docs/en/zos/latest?topic=reporting-scrt-overview"},
            {"title": "StackMF Mainframe Modernization and Cost Optimization", "url": "https://stackmf.com/#tco-calculator"}
        ]
    },
    {
        "slug": "cics-storage-violation-aica-runaway-task",
        "title": "Diagnosing CICS AICA (Runaway Task) and Storage Violations (Subpool Overwrites)",
        "category": "ABENDS & Diagnostics",
        "tags": ["CICS", "AICA", "Storage Violation", "Runaway Task", "Subpool", "Dump Analysis"],
        "reading_time": "10 min read",
        "date": "2026-09-27",
        "tldr": "CICS ABEND AICA halts transactions that loop without yielding CPU control to CICS task dispatcher, while storage violations corrupt transaction work areas. Discover how to inspect the CICS System Dump, identify runaway loops, and configure storage protection keys.",
        "problem": """High-priority CICS transactions suddenly terminate with:
```text
DFHPC2034 10:14:22 CICS01 TASK 04921 TRANSACTION TXOR ABENDED AICA.
          TIME LIMIT EXCEEDED WITHOUT RETURNING CONTROL TO CICS.
```
In other instances, the entire CICS region writes message DFHSR0601 A storage violation has occurred in module DFHXMDS, forcing emergency region cycling during peak trading hours.""",
        "root_cause": """CICS uses cooperative multitasking:
1. **AICA (Runaway Task)**: If an application COBOL program enters an infinite PERFORM loop or scans large tables without issuing a CICS command (such as EXEC CICS DELAY, EXEC CICS RECEIVE, or EXEC CICS SUSPEND), the CICS dispatcher timer expires (defined by RUNAWAY interval in the SIT, typically 5000ms), and CICS purges the task.
2. **Storage Violation**: An application program writes beyond the boundary of its allocated DFHCOMMAREA, CICS CONTAINER, or GETMAIN storage, overwriting the Storage Accounting Area (SAA) check-bytes of an adjacent task's memory.""",
        "solution": """### 1. Locate the Infinite Loop in CICS Dump
Check the offset where the task was interrupted:
```text
PSW AT TIME OF INTERRUPT: 078D1000 84C2145A
TASK CPU TIME USED: 5.002 SECONDS (EXCEEDED RUNAWAY 5000MS)
```
Map the offset 84C2145A to the compiler listing. Typically, an un-incremented counter in an UNTIL loop is the culprit.

### 2. Yield CPU Control in Long-Running Transactions
If a transaction must process a large array in memory, issue periodic yields:
```cobol
       ADD 1 TO WS-CHUNK-COUNT
       IF WS-CHUNK-COUNT > 500
           EXEC CICS SUSPEND END-EXEC
           MOVE 0 TO WS-CHUNK-COUNT
       END-IF.
```

### 3. Activate CICS Storage Protection & Transaction Isolation
In the CICS System Initialization Table (SIT):
- Set STGPROT=YES
- Set TRANISO=YES
This prevents an errant User-Key transaction from corrupting other concurrent tasks or CICS system subpools!""",
        "prevention": [
            "Set appropriate RUNAWAY transaction limits in CSD definitions (e.g., 2000-5000ms).",
            "Enable CICS Storage Protection (STGPROT=YES) across all production regions.",
            "Verify subscript boundaries on all MOVE statements to avoid SAA header corruption.",
            "Include EXEC CICS SUSPEND in CPU-bound batch-in-online algorithms."
        ],
        "references": [
            {"title": "IBM CICS TS: Dealing with Runaway Tasks (AICA)", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=dumps-investigating-aica-abend"},
            {"title": "IBM CICS TS: Storage Violations and Recovery", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=dumps-investigating-storage-violations"},
            {"title": "StackMF 24/7 Managed Application Maintenance (AMS)", "url": "https://stackmf.com/#maintenance-ams"}
        ]
    },
    {
        "slug": "db2-rebind-stability-package-plan-switching",
        "title": "Mastering DB2 Package Plan Stability: Avoiding Access Path Regressions During REBIND",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "Plan Stability", "REBIND", "Access Paths", "APREUSE", "PLANMGMT"],
        "reading_time": "9 min read",
        "date": "2026-09-27",
        "tldr": "Rebinding DB2 packages after software maintenance or schema changes can cause access path regressions, resulting in sudden 10x query slowdowns. Master DB2 Plan Management (PLANMGMT), APREUSE, and catalog switching to safeguard production workloads.",
        "problem": """Following a quarterly DB2 maintenance migration or catalog RUNSTATS update, an automated mass REBIND job runs. The next morning, high-throughput OLTP transactions stall:
```text
DSNA672I SQL QUERY RUNTIME JUMPED FROM 12MS TO 4800MS
PLAN_TABLE SHOWS ACCESS PATH SWITCHED FROM MATCHING INDEX SCAN TO TABLESPACE SCAN
```
Database administrators face severe business escalation while attempting to pinpoint which packages regressed.""",
        "root_cause": """During REBIND PACKAGE, DB2 re-evaluates all access paths based on current catalog statistics and optimizer algorithms. If statistics changed slightly or a different index path is estimated marginally cheaper, the optimizer selects a new path. In complex multi-table joins, the new estimate may result in disastrous access path regression.""",
        "solution": """### 1. Bind with PLANMGMT(EXTENDED)
Configure DB2 Plan Management to retain current, previous, and original package copies:
```text
REBIND PACKAGE(DSN8D13A.CUST01) -
       PLANMGMT(EXTENDED) -
       APREUSE(WARN)
```

### 2. Instant Access Path Fallback via SWITCH
If a newly bound package exhibits poor response times, instantly revert without recompiling:
```text
REBIND PACKAGE(DSN8D13A.CUST01) -
       SWITCH(PREVIOUS)
```
Within 2 seconds, DB2 switches back to the previous proven access path in the catalog, restoring production immediately!

### 3. Verify Package Copies in Catalog
Query package stability history:
```sql
SELECT BIND_TIME, PLANMGMT, APREUSE_SUCCESS
FROM SYSIBM.SYSPACKAGE
WHERE NAME = 'CUST01';
```""",
        "prevention": [
            "Always rebind critical production packages with PLANMGMT(EXTENDED).",
            "Use APREUSE(ERROR) or APREUSE(WARN) to detect unexpected access path deviations before cutover.",
            "Test rebinds in a cloned pre-production subsystem before executing across production.",
            "Use DB2 Query Capture and Comparison utilities to validate elapsed-time impact."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS Managing Performance: Access Path Stability", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=performance-access-path-stability"},
            {"title": "IBM Db2 13 for z/OS REBIND PACKAGE Command", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=commands-rebind-package-db2"},
            {"title": "StackMF Enterprise Mainframe Modernization Services", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },
    {
        "slug": "cobol-null-indicators-db2-host-variables",
        "title": "Handling DB2 SQLCODE -305: Null Indicator Variables in COBOL Working-Storage",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "COBOL", "SQLCODE -305", "Null Indicator", "Host Variables"],
        "reading_time": "8 min read",
        "date": "2026-09-27",
        "tldr": "DB2 SQLCODE -305 is raised when a query attempts to retrieve a NULL column value into a COBOL host variable without specifying an accompanying Null Indicator variable. Learn proper indicator syntax and default coalescing.",
        "problem": """A COBOL DB2 batch program runs smoothly in testing but fails in production when processing a newly created customer record:
```text
DSNT408I SQLCODE = -305, ERROR:  THE NULL VALUE CANNOT BE ASSIGNED TO A HOST
         VARIABLE IN POSITION 4 BECAUSE NO INDICATOR VARIABLE IS SPECIFIED.
DSNT418I SQLSTATE = 22002 SQLSTATE RETURN CODE
CEE3250C The system or user abend U4038 was issued.
```
The job halts, rolling back earlier batch changes.""",
        "root_cause": """Relational databases support NULL (the absence of any value), whereas COBOL has no intrinsic concept of null memory—every memory location contains bits (spaces, zeroes, etc.).
When DB2 encounters a NULL column during a FETCH or SELECT INTO:
- If the SQL statement provides a companion Indicator Variable (:VAR :IND), DB2 sets the indicator to -1 (Null) and leaves the host variable undisturbed.
- If no indicator variable was supplied on a nullable column, DB2 raises SQLCODE -305 to prevent undefined data corruption.""",
        "solution": """### 1. Declare Indicator Variables in Working-Storage
Define null indicators as 2-byte binary signed integers (PIC S9(4) COMP):
```cobol
       01  WS-CUSTOMER-DATA.
           05  WS-CUST-ID               PIC X(10).
           05  WS-PHONE-NUMBER          PIC X(15).
           05  WS-PHONE-IND             PIC S9(4) COMP.
           05  WS-CREDIT-SCORE          PIC S9(4) COMP.
           05  WS-CREDIT-IND            PIC S9(4) COMP.
```

### 2. Include Indicators in SELECT Statements
Attach the indicator variable immediately after the host variable:
```cobol
       EXEC SQL
           SELECT CUST_ID, PHONE_NUMBER, CREDIT_SCORE
           INTO :WS-CUST-ID,
                :WS-PHONE-NUMBER :WS-PHONE-IND,
                :WS-CREDIT-SCORE :WS-CREDIT-IND
           FROM CUSTOMER_TABLE
           WHERE CUST_ID = :WS-CUST-ID
       END-EXEC.
```

### 3. Evaluate Indicator Values in COBOL Logic
```cobol
       IF WS-PHONE-IND < 0
           MOVE 'NO PHONE ON FILE' TO WS-DISPLAY-PHONE
       ELSE
           MOVE WS-PHONE-NUMBER    TO WS-DISPLAY-PHONE
       END-IF.
```""",
        "prevention": [
            "Check the DB2 DCLGEN output: any column defined with NULL requires an indicator variable in COBOL.",
            "Use COALESCE or IFNULL in SQL when sensible default values exist.",
            "Verify all external fields during unit tests using test cases with empty/null columns."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS Codes: SQLCODE -305", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=codes-305"},
            {"title": "IBM Enterprise COBOL for z/OS: Using DB2 Indicator Variables", "url": "https://www.ibm.com/docs/en/cobol-zos/latest?topic=sql-indicator-variables"}
        ]
    }
]
