# blogs_data_queue.py - Comprehensive Production Mainframe Runbooks for Daily Autonomous Publishing

QUEUED_ARTICLES = [
    {
        "slug": "zowe-cli-cics-newcopy-automation-pipeline",
        "title": "Automating CICS NEWCOPY and PHASEIN in Git CI/CD Pipelines with Zowe CLI",
        "category": "DevOps & Automation",
        "tags": ["Zowe CLI", "CICS TS", "NEWCOPY", "PHASEIN", "CI/CD", "DevOps", "Automation"],
        "reading_time": "9 min read",
        "tldr": "Manual CEMT SET PROGRAM NEWCOPY commands slow deployment velocity and introduce human error. Learn how to securely automate CICS NEWCOPY and PHASEIN via Zowe CLI and GitHub Actions, enabling zero-downtime application refresh upon Git pull request merge.",
        "problem": """Mainframe application teams deploying COBOL/CICS changes manually log into 3270 green screens, navigate to CICS regions, and issue:
```text
CEMT SET PROGRAM(ORDR01) NEWCOPY
```
In multi-region CICS configurations (AOR/TOR/DOR Sysplex), engineers frequently forget secondary regions, leading to version skew where users encounter stale code or `AEIS` abends. Furthermore, if the program is actively executing, `NEWCOPY` fails with `INVREQ`, disrupting deployments.""",
        "root_cause": """`NEWCOPY` cannot refresh a program in storage if the current use count (`USECOUNT`) is greater than zero, or if tasks are suspended inside the module. In contrast, `PHASEIN` allows active tasks to finish executing the old copy while routing new transactions to the freshly loaded module in the DFHRPL concatenation. Manual execution across dozens of regions lacks concurrency control, audit logging, and automated rollback upon failure.""",
        "solution": """### 1. Configure Zowe CICS Profile via Zowe CLI
Create a dedicated z/OSMF or CICS Management Client Interface (CMCI) profile:
```bash
zowe profiles create cics-profile cics_prod \\
  --host zos.production.corp \\
  --port 4443 \\
  --user PRODDEPLOY \\
  --password "$DEPLOY_TOKEN" \\
  --region-name CICS* \\
  --protocol https
```

### 2. Issue CICS PHASEIN Across All Target Regions
Execute `cics refresh program` using PHASEIN to guarantee zero transaction downtime:
```bash
# Refresh ORDR01 across all Application Owning Regions (AORs)
zowe cics refresh program ORDR01 \\
  --region-name "AOR*" \\
  --cics-profile cics_prod
```
The CLI returns JSON metadata confirming the load point, length, and timestamp of the new binary:
```json
{
  "response": "OK",
  "program": "ORDR01",
  "action": "PHASEIN",
  "regions_updated": ["AOR01", "AOR02", "AOR03"],
  "useCount": 0
}
```

### 3. Integrate into GitHub Actions / GitLab CI Pipeline
```yaml
name: Deploy COBOL to CICS
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install Zowe CLI
        run: npm install -g @zowe/cli @zowe/cics-for-zowe-cli
      - name: Deploy Binary & Refresh CICS
        env:
          ZOWE_OPT_USER: ${{ secrets.ZOS_DEPLOY_USER }}
          ZOWE_OPT_PASSWORD: ${{ secrets.ZOS_DEPLOY_PWD }}
        run: |
          zowe zos-files upload file-to-data-set dist/ORDR01.load "PROD.CICS.LOADLIB(ORDR01)"
          zowe cics refresh program ORDR01 --region-name "AOR*"
```""",
        "prevention": [
            "Prefer `PHASEIN` over `NEWCOPY` for live production programs to avoid task locking.",
            "Verify that `RESSEC(NO)` or proper RACF permissions for the deploy service account exist in the CICS region.",
            "Incorporate automated post-deploy smoke tests using Zowe REST API mocks.",
            "Include CICS region discovery in pipeline scripts to automatically refresh newly provisioned regions."
        ],
        "references": [
            {"title": "IBM CICS TS: CEMT SET PROGRAM Options (NEWCOPY vs PHASEIN)", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=commands-cemt-set-program"},
            {"title": "Open Mainframe Project: Zowe CLI CICS Plugin Documentation", "url": "https://docs.zowe.org/stable/user-guide/cics-cli-plugin"},
            {"title": "StackMF DevOps & Modern Mainframe Pods", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },
    {
        "slug": "ezt-virtual-files-imu-memory-optimization",
        "title": "Optimizing Easytrieve VIRTUAL File Translations in IMU: Minimizing Work Spool DASD",
        "category": "Modernisation & Cloud",
        "tags": ["Easytrieve", "IMU", "Virtual Files", "COBOL", "Memory Optimization", "DASD"],
        "reading_time": "10 min read",
        "tldr": "Migrating Easytrieve (EZT) legacy scripts to IBM Migration Utility (IMU) frequently creates massive intermediate DASD work files for VIRTUAL files. Discover how to tune EASYTRAN options, leverage 64-bit in-memory tables, and eliminate hundreds of gigabytes in batch spool allocation.",
        "problem": """During an enterprise migration from Broadcom Easytrieve Classic to IBM Migration Utility (IMU / EASYTRAN), converted batch jobs experience severe DASD consumption:
```text
IEC030I B37-04,IFG0554A,JOBE012,STEP01,FSRTWORK,1402,PROD01,SYS26281.T091214.RA000.JOBE012.R0100001
FSORT001E WORK DATA SET FULL. UNABLE TO COMPLETE VIRTUAL SORT.
```
Jobs that previously executed in 4 minutes with native Easytrieve run for 35 minutes under IMU, allocating up to 80GB of temporary scratch space across JES spool and DFSMS volumes.""",
        "root_cause": """Easytrieve programs frequently declare:
```text
FILE VIRTFILE VIRTUAL
```
Native Easytrieve manages small virtual files in below-the-bar virtual storage. When IMU translates `VIRTUAL` files into generated COBOL, its default configuration directs records to intermediate temporary disk files (`FSRTWORK` / `SYSUT1`) and triggers physical DFSORT work datasets unless explicit in-memory options are enabled in `EASYTRAN` options.""",
        "solution": """### 1. Adjust EASYTRAN Compiler Options
In the IMU translation step, pass the `MEMORY` and `VIRTUAL=MEMORY` parameters:
```jcl
//TRANSLAT EXEC PGM=FSYACC00,
// PARM=('EASYTRAN',
//       'VIRTUAL=MEMORY',
//       'FSORT=INTERNAL',
//       'NOWORKFILE')
```
- `VIRTUAL=MEMORY`: Instructs IMU to generate in-memory COBOL working storage tables with `OCCURS DEPENDING ON` rather than temporary sequential datasets.
- `FSORT=INTERNAL`: Leverages DFSORT hiperspaces and memory buffers rather than physical DASD work units.

### 2. Configure 64-Bit Memory Allocation in Generated COBOL
Ensure the target Enterprise COBOL compiler step utilizes 64-bit or Extended Addressing (AMODE 31/64):
```jcl
//COMPILE EXEC PGM=IGYCRCTL,
// PARM=('ARCH(13)','ARITH(EXTEND)','OPT(2)','LP(64)')
```

### 3. Generated COBOL Architecture Comparison
Instead of physical I/O writes:
```cobol
      * DEFAULT UNOPTIMIZED TRANSLATION:
       WRITE VIRTUAL-REC TO FSRTWORK-FILE.

      * OPTIMIZED IN-MEMORY TRANSLATION:
       ADD 1 TO WS-VIRTUAL-INDEX
       MOVE INPUT-DATA TO WS-VIRTUAL-TABLE(WS-VIRTUAL-INDEX).
```
This reduces execution time by up to 88% and eliminates temporary DASD allocation entirely!""",
        "prevention": [
            "Benchmark record counts before setting `VIRTUAL=MEMORY` to prevent out-of-region S878 abends.",
            "Standardize `EASYTRAN` site options in `FSYPROCS` rather than per-job JCL overrides.",
            "Verify DFSORT hiperspace allocation quotas with your z/OS storage administration team.",
            "Audit converted Easytrieve programs for redundant sorting passes."
        ],
        "references": [
            {"title": "IBM Migration Utility for z/OS User's Guide (IMU V5.1)", "url": "https://www.ibm.com/docs/en/migration-utility/5.1"},
            {"title": "Broadcom Easytrieve Report Generator Syntax Reference", "url": "https://techdocs.broadcom.com/us/en/ca-mainframe-software/devops/easytrieve-report-generator/11-6.html"},
            {"title": "StackMF EZT to IMU Automated Modernization Services", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },
    {
        "slug": "vscode-zowe-jcl-formatting-validation-extension",
        "title": "Real-Time JCL Syntax Validation, Parameter Linting, and Formatting in VS Code",
        "category": "DevOps & Automation",
        "tags": ["VS Code", "Zowe", "JCL Linter", "Syntax Validation", "DevOps", "Modernisation"],
        "reading_time": "8 min read",
        "tldr": "Submitting JCL with mismatched quotes or misplaced continuation characters wastes hours in batch turnaround cycles. Discover how to configure real-time JCL linting, JES2/JES3 syntax validation, and automated column-72 alignment inside Visual Studio Code.",
        "problem": """Developers write JCL on modern workstations and submit jobs via Zowe CLI or ISPF, only to receive immediate JCL errors:
```text
IEF605I UNIDENTIFIED OPERATION FIELD ON EXEC STATEMENT
IEF621I EXPECTED CONTINUATION NOT RECEIVED ON DD STATEMENT
```
Waiting for JES2 job queue turnaround for basic syntax typos cripples developer feedback loops and destroys pipeline velocity.""",
        "root_cause": """JCL is column-strict:
- Statements must start with `//` in columns 1-2.
- Name field begins in column 3.
- Parameter continuations must break after a comma, place non-blank characters in column 72 (or leave blank depending on JES rules), and resume between columns 4 and 16.
Traditional text editors lack language server protocol (LSP) understanding of these 80-byte card image constraints.""",
        "solution": """### 1. Install the Mainframe JCL Extension Pack
In VS Code, install:
- **Zowe Explorer** (`Zowe.vscode-extension-for-zowe`)
- **IBM Z Open Editor** (`IBM.zopeneditor`) or **Broadcom JCL Language Support**

### 2. Configure Settings for 80-Column Punch Card Rules
In your `.vscode/settings.json`:
```json
{
  "editor.rulers": [71, 72, 80],
  "editor.renderWhitespace": "all",
  "[jcl]": {
    "editor.insertSpaces": true,
    "editor.tabSize": 2,
    "editor.wordWrap": "off"
  },
  "zopeneditor.jcl.linting.enabled": true,
  "zopeneditor.jcl.datasetCheck": true
}
```

### 3. Pre-Flight Remote JCL Validation via Zowe CLI
Before submitting to execution queues, run a TYPRUN=SCAN syntax validation:
```bash
zowe zos-jobs submit local-file ./deploy.jcl \\
  --jcl-symbols "TYPRUN=SCAN" \\
  --wait-for-active
```
If errors exist, the spool returns line-numbered diagnostics without executing a single step!""",
        "prevention": [
            "Configure pre-commit git hooks to run `jcl-lint` across all repo members.",
            "Enforce column 72 visual boundary rulers in developer workstation templates.",
            "Avoid trailing spaces on continuation lines.",
            "Use symbolic JCL variables (`&SYSUID`, `&HLQ`) to standardize parameter lengths."
        ],
        "references": [
            {"title": "IBM z/OS MVS JCL Reference: Continuation Rules", "url": "https://www.ibm.com/docs/en/zos/latest?topic=rules-continuation"},
            {"title": "IBM Z Open Editor JCL Language Capabilities", "url": "https://www.ibm.com/docs/en/z-open-editor/latest"},
            {"title": "StackMF Mainframe Modernization & Developer Experience", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },
    {
        "slug": "idz-telemetry-metrics-developer-productivity-dashboard",
        "title": "Measuring Mainframe Developer Velocity: Tracking IDz and Zowe Adoption Metrics",
        "category": "DevOps & Automation",
        "tags": ["IDz", "Developer Productivity", "Telemetry", "Code Metrics", "DORA", "Git"],
        "reading_time": "11 min read",
        "tldr": "Mainframe modernization programs frequently struggle to quantify ROI. Learn how to implement telemetry across IBM Developer for z/OS (IDz), Zowe CLI, and Git pipelines to measure developer build frequency, lead time to production, and green-screen exit velocity.",
        "problem": """Leadership invests millions in modern mainframe IDEs (IDz, VS Code, Git) to replace ISPF 3270, but 6 months later, nobody knows if developers are actually using the tools or if code velocity has improved:
```text
EXECUTIVE AUDIT QUERY: What is the adoption percentage of IDz vs ISPF?
ANSWER: Unknown. No centralized telemetry or DORA metrics tracked.
```
Without data, license renewals for legacy tools continue unnecessarily.""",
        "root_cause": """Mainframe environments traditionally lack client-side telemetry. Developers switch back to ISPF out of muscle memory, while management lacks visibility into cycle times, build frequencies, or automated test coverage.""",
        "solution": """### 1. Enable IBM Developer for z/OS Usage Telemetry
Configure IDz client workspace metrics to stream to enterprise dashboards:
In `rse.env`:
```text
_RSE_TELEMETRY_LOG=/var/log/idz/telemetry.log
_RSE_COLLECT_USAGE_METRICS=TRUE
```

### 2. Track Zowe CLI Command Frequency
Capture CLI invocations in corporate CI/CD runners:
```bash
# In corporate wrapper script or shell profile:
export ZOWE_APP_TELEMETRY=true
export ZOWE_LOG_LEVEL=INFO
```
Parse logs to measure jobs submitted, datasets edited, and API invocations per developer per week.

### 3. Core DORA Metrics for Mainframe Engineering
Track four essential benchmarks:
1. **Deployment Frequency**: How often COBOL/PL/I packages are released to production (target: weekly vs quarterly).
2. **Lead Time for Changes**: Hours elapsed from Git commit to CICS/IMS promotion.
3. **Change Failure Rate**: Percentage of deployments triggering an immediate rollback or emergency fix.
4. **Time to Restore Service (MTTR)**: Elapsed time to resolve an abend in production.""",
        "prevention": [
            "Establish monthly developer training pods to help engineers transition from ISPF.",
            "Decommission legacy ISPF edit macros when equivalent VS Code / IDz snippets are ready.",
            "Correlate tool adoption with developer satisfaction surveys.",
            "Reward pods that achieve 100% automated Git deployment pipelines."
        ],
        "references": [
            {"title": "IBM Developer for z/OS (IDz) Administration Guide", "url": "https://www.ibm.com/docs/en/developer-for-zos"},
            {"title": "DORA State of DevOps Metrics for Enterprise Mainframes", "url": "https://cloud.google.com/devops"},
            {"title": "StackMF Dual-Stack Engineering Pod Velocity", "url": "https://stackmf.com/#team-builder"}
        ]
    },
    {
        "slug": "db2-hash-access-vs-index-access-z16",
        "title": "DB2 for z/OS Access Paths: When to Leverage Hash Access vs Traditional Index Scans",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2 for z/OS", "Hash Access", "Index Access", "z16 Architecture", "SQL Tuning", "CPU Optimization"],
        "reading_time": "9 min read",
        "tldr": "Direct singleton key lookups in DB2 for z/OS can bypass index tree traversal via Hash Access, saving CPU cycles on IBM z16 processors. Understand when hash organization beats B-tree indexes and when it degrades range query performance.",
        "problem": """High-frequency OLTP transactions querying customer or account tables by primary key consume excessive CPU:
```text
DSNX001I SQL SELECT ELAPSED TIME: 1.2MS (3 INDEX LEVELS TRAVERSED)
TRANSACTION VOLUME: 45,000 TRANSACTIONS / SEC
PEAK 4HRA CPU UTILIZATION: 94% ON GENERAL PROCESSORS
```
At scale, traversing 3 to 4 B-tree index levels for every single row query creates significant CPU overhead.""",
        "root_cause": """Standard DB2 tables utilize B-tree indexes where the optimizer reads root, intermediate, and leaf index pages before reading the actual data page (3-4 getpage requests per query). Hash access calculates an algorithmic page offset directly from the hash key, reducing the operation to a single getpage for matching rows.""",
        "solution": """### 1. Define Hash Organization on Tablespace
```sql
ALTER TABLESPACE DBNAME.CUSTTS
  ORGANIZATION HASH UNIQUE (CUST_ID)
  HASH SPACE 500M;
```

### 2. Verify Access Path in EXPLAIN PLAN_TABLE
Query the DB2 catalog plan table for your queries:
```sql
SELECT QUERYNO, ACCESSTYPE, MATCHCOLS, ACCESSNAME
FROM PLAN_TABLE
WHERE QUERYNO = 101;
```
- `ACCESSTYPE = 'H'`: Hash access successfully chosen by the optimizer!
- Getpage count drops from 4 to 1.

### 3. When NOT to Use Hash Access
- Tables frequently subjected to range queries (`WHERE CUST_ID BETWEEN 1000 AND 2000`). Hash access does not support range scans.
- Tables with unpredictable, explosive growth beyond the defined `HASH SPACE`.
- Tables where mass inserts cause excessive hash collision overflow records.""",
        "prevention": [
            "Reserve Hash Access strictly for stable, high-volume singleton lookup tables.",
            "Monitor hash overflow records using DB2 `RUNSTATS` and `SYSTABLESPACESTATS`.",
            "Reorganize hash tablespaces if overflow percentage exceeds 10%.",
            "Evaluate IBM z16 System Recovery Boost and on-chip AI accelerators for complementary savings."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS Performance Guide: Hash Organization", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=organization-hash-access"},
            {"title": "IBM Redbook: Db2 for z/OS Best Practices for High Throughput", "url": "https://www.redbooks.ibm.com/"},
            {"title": "StackMF DB2 Performance Tuning & Modernization", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },
    {
        "slug": "cics-liberty-java-spring-boot-zero-mlc",
        "title": "Running Java Spring Boot Microservices inside CICS Liberty on zIIP Engines at Zero MLC",
        "category": "Modernisation & Cloud",
        "tags": ["CICS TS", "Liberty JVM", "Spring Boot", "zIIP", "Zero MLC", "Java", "Modernisation"],
        "reading_time": "11 min read",
        "tldr": "Enterprise mainframe bills are driven by Monthly License Charge (MLC) on general-purpose processors (CPs). Learn how deploying Java Spring Boot microservices inside CICS Liberty redirects workload to 100% zIIP engines, slashing IBM software licensing costs.",
        "problem": """Digital transformation teams build cloud microservices that constantly query mainframe CICS transactions via network APIs, driving up general CP utilization:
```text
SCRT MONTHLY REPORT:
MSU PEAK COINCIDES WITH REST API INGESTION SPIKE (+180 MSUs)
ESTIMATED IBM MLC ESCALATION: $32,000 / MONTH
```
CIOs face escalating costs simply because external APIs trigger transactional CPU on general mainframe cores.""",
        "root_cause": """Traditional COBOL and CICS programs execute on standard CP engines, which count toward the enterprise Rolling 4-Hour Average (R4HA) MSU rating. In contrast, Java workloads running inside an IBM z/OS Java Virtual Machine (JVM) are up to 99% offloadable to IBM System z Integrated Information Processors (zIIP), which carry zero IBM software MLC cost.""",
        "solution": """### 1. Configure CICS Liberty JVM Server
In your CICS system initialization and CSD, define the JVM profile:
```text
DEFINE JVMSERVER(DFH$WLP) GROUP(LIBERTY)
  JVMPROFILE(DFH$WLP)
  STATUS(ENABLED)
```
In `DFH$WLP.jvmprofile`:
```properties
JAVA_HOME=/usr/lpp/java/J8.0_64
WLP_INSTALL_DIR=/usr/lpp/cics/wlp
-Dcom.ibm.cics.jvmserver.wlp.autoconfigure=true
-Xms512m -Xmx2048m
```

### 2. Deploy Spring Boot Application to CICS Liberty
Package your Spring Boot microservice as a WAR or Liberty drop-in application and deploy via CICS bundle:
```bash
zowe zos-files upload file-to-data-set target/account-service.war \\
  "/var/cicsts/liberty/dropins/account-service.war" --binary
```

### 3. Verify zIIP Offload in SDSF
Check the RMF / SDSF `DA` display:
```text
JOBNAME  STEPNAME  CPU%  zIIP%  zIIP-CP%
CICS01   CICS      0.4   38.2   0.0
```
Over 98% of the Java execution executes on zIIP engines, keeping general CP utilization flat and preserving MLC baselines!""",
        "prevention": [
            "Ensure CICS JCICS API calls are threadsafe to prevent switching from zIIP to standard CP.",
            "Size JVM garbage collection pauses using IBM GCMV (Garbage Collection and Memory Visualizer).",
            "Monitor zIIP-on-CP spilling in RMF reports to ensure adequate zIIP engine capacity.",
            "Implement connection pooling for Db2 type 4 JDBC drivers inside Liberty."
        ],
        "references": [
            {"title": "IBM CICS TS: Java Applications in CICS with Liberty", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=java-cics-liberty-jvm-server"},
            {"title": "IBM Redbook: Java and zIIP Performance on z/OS", "url": "https://www.redbooks.ibm.com/"},
            {"title": "StackMF Mainframe to Cloud Hybrid Architecture", "url": "https://stackmf.com/#fullstack-bridge"}
        ]
    },
    {
        "slug": "vsam-linear-datasets-lds-db2-internals",
        "title": "Understanding VSAM Linear Data Sets (LDS): How DB2 and MQ Manage Physical Storage",
        "category": "CICS & VSAM Architecture",
        "tags": ["VSAM LDS", "DB2 Tablespaces", "Control Intervals", "IDCAMS", "Storage", "z/OS"],
        "reading_time": "9 min read",
        "tldr": "Unlike KSDS or ESDS files, VSAM Linear Data Sets (LDS) contain no embedded record descriptors and store raw byte streams in 4KB multiples. Discover how DB2 for z/OS and IBM MQ exploit LDS for high-speed page-level I/O and how to diagnose allocation failures.",
        "problem": """A database administrator creates a new partition for a multi-terabyte DB2 tablespace, but the allocation job abends:
```text
DSNP001I -DB2P DSNPCMT0 - INSERT LOGICAL ERROR ON DSN8D13A.DSN8S13E.I0001.A001
IEC161I 037(050,004)-084,DB2MSTR,DB2MSTR,SYS00001,,,DSN8D13A...
DSNP007I -DB2P EXTEND FAILED FOR DSN8D13A.DSN8S13E
```
The application team cannot determine whether the fault lies within DB2 catalog permissions or VSAM storage limits.""",
        "root_cause": """DB2 tablespaces and indexspaces, as well as IBM MQ page sets, are built on physical VSAM Linear Data Sets (LDS). An LDS consists exclusively of unformatted Control Intervals (CIs) in multiples of 4,096 bytes (4KB, 8KB, 16KB, 32KB). Unlike KSDS files, an LDS contains no Record Definition Fields (RDFs) or Control Interval Definition Fields (CIDFs).
Allocation failures occur when:
1. Secondary allocation extents exceed the volume limit (123 extents on non-SMS or 255 on SMS).
2. The dataset exceeds 4GB without being assigned an SMS Dataclass with `EXTENDED ADDRESSABILITY (EA)`.""",
        "solution": """### 1. Inspect LDS Definition with IDCAMS LISTCAT
```jcl
//LISTLDS EXEC PGM=IDCAMS
//SYSPRINT DD SYSOUT=*
//SYSIN    DD *
  LISTCAT ENTRIES('DSN8D13A.DSN8S13E.I0001.A001') ALL
/*
```
Check `EXTENTS` and `DATACLASS`. If the dataset stopped at 4,194,304 KB, Extended Addressability is missing!

### 2. Define SMS Data Class for Extended Addressability (EA)
Ensure your DFSMS configuration defines:
```text
DATA CLASS: DBMCEAO
  DATA SET NAME TYPE: EXTENDED
  EXTENDED ADDRESSABILITY: Y
```

### 3. Native IDCAMS DEFINE CLUSTER for Linear Data Set
```jcl
//DEFLDS  EXEC PGM=IDCAMS
//SYSPRINT DD SYSOUT=*
//SYSIN    DD *
  DEFINE CLUSTER -
    (NAME(PROD.MQ.PAGESET01) -
     LINEAR -
     CYLINDERS(500 100) -
     VOLUME(VOL001) -
     DATACLASS(DBMCEAO) -
     SHAREOPTIONS(2 3))
/*
```""",
        "prevention": [
            "Always assign an EA-enabled SMS Dataclass to DB2 and MQ LDS allocations.",
            "Monitor extent counts using automated DFSMSrmm or catalog health scripts.",
            "Avoid placing high-write DB2 LDS partitions on contiguous over-allocated volumes.",
            "Use VSAM Space Constraint Relief (`SPACE_CONSTRAINT_RELIEF=YES`) in SMS to avoid B37 abends."
        ],
        "references": [
            {"title": "IBM DFSMS: Using Data Sets (VSAM Linear Data Sets)", "url": "https://www.ibm.com/docs/en/zos/latest?topic=datasets-linear-data-sets"},
            {"title": "IBM Db2 13 for z/OS Managing Storage: Tablespace Datasets", "url": "https://www.ibm.com/docs/en/db2-for-zos/13"},
            {"title": "StackMF Mainframe Core Systems Architecture", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },
    {
        "slug": "ims-fast-path-dedb-online-utility-tuning",
        "title": "Tuning IMS Fast Path DEDB High-Speed Reorganization (HSRE) for 24/7 Availability",
        "category": "CICS & VSAM Architecture",
        "tags": ["IMS Fast Path", "DEDB", "High Speed Reorg", "OLR", "Database Tuning", "z/OS"],
        "reading_time": "10 min read",
        "tldr": "IMS Fast Path Data Entry Databases (DEDBs) power ultra-high-volume financial ledgers. Master the High-Speed DEDB Reorganization (HSRE) utility to reclaim fragmented independent overflow (IOVF) space online without interrupting 24/7 banking transactions.",
        "problem": """High-frequency IMS Fast Path banking transactions begin experiencing elevated lock wait times and abends:
```text
DFS0534I IOVF EXTENSION FAILED FOR AREA AREA01 DEDB DEDB01. NO AVAILABLE CI.
ABEND U0844 UNABLE TO ALLOCATE INDEPENDENT OVERFLOW BUFFER
```
Database administrators face urgent pressure to reorganize the DEDB, but the financial ledger operates 24/7 with zero scheduled downtime.""",
        "root_cause": """DEDB areas are divided into:
1. Root Addressable Part (RAP).
2. Sequential Dependent (SDEP) segment space.
3. Independent Overflow (IOVF) space.
When rapid updates cause frequent segment splits, IOVF control intervals become exhausted. Traditional offline reorgs require taking the area offline with `/STOP AREA`, cutting off banking transactions.""",
        "solution": """### 1. Run Online High-Speed DEDB Reorganization (HSRE)
The High-Speed DEDB Reorganization utility (`DBFUHDR0`) reorganizes one Unit of Work (UOW) at a time while concurrent transactions continue accessing other UOWs:
```jcl
//ONLINEHS EXEC PGM=DFSRRC00,
// PARM='FP,DBFUHDR0,DEDB01,,,,,,,,,,,,'
//STEPLIB  DD DSN=IMS.SDFSRESL,DISP=SHR
//SYSIN    DD *
  AREA AREA01
  TYPE HSRE
/*
```

### 2. Verify UOW Locks and Buffer Pools
To prevent contention with live OLTP transactions:
- Configure `BUFALLO=20` and `BUFPROC=10` in the utility control cards.
- Utility acquires short-duration locks only on the individual UOW being reorganized.

### 3. Monitor Reclaimed IOVF Space
```text
DFS2641I HSRE UTILITY COMPLETED FOR AREA AREA01.
TOTAL UOWS REORGANIZED: 1,240
IOVF CIS RECLAIMED: 842
FREE SPACE RECOVERED: 3.4 MB
```
The area remains online throughout the entire execution!""",
        "prevention": [
            "Schedule automated HSRE runs during lower-volume night intervals.",
            "Monitor IOVF consumption thresholds via automated IMS Fast Path utility reports.",
            "Re-evaluate area randomized RAP parameters if IOVF overflows exceed 25% within days.",
            "Ensure shared secondary storage buffers are pre-allocated in IMS SEDA options."
        ],
        "references": [
            {"title": "IBM IMS 15.3 Database Administration: High-Speed DEDB Reorganization", "url": "https://www.ibm.com/docs/en/ims/15.3?topic=utilities-high-speed-dedb-reorganization-utility-dbfuhdr0"},
            {"title": "IBM Redbook: Fast Path Performance and Tuning Guide", "url": "https://www.redbooks.ibm.com/"},
            {"title": "StackMF 24/7 Managed Application Maintenance (AMS)", "url": "https://stackmf.com/#maintenance-ams"}
        ]
    },
    {
        "slug": "ca-7-virtual-resource-management-vrm-contention",
        "title": "Troubleshooting CA-7 Virtual Resource Management (VRM) Enqueue Locks and Depths",
        "category": "DevOps & Automation",
        "tags": ["CA-7", "VRM", "Workload Automation", "Enqueue Locks", "Batch Tuning", "Scheduling"],
        "reading_time": "9 min read",
        "tldr": "Jobs in CA-7 frequently stall in the Ready Queue with VRM (Virtual Resource Management) dependencies, delaying overnight batch windows. Learn how to query resource queues, resolve exclusive lock contention, and plan migration to modern schedulers.",
        "problem": """Overnight batch processing grinds to a halt. In the CA-7 3270 console, dozens of critical payroll and settlement jobs sit in the Ready Queue without starting:
```text
JOB       JOB#   QUEUE  STATUS   REASON
PAYROLL1  4821   RDY    W-RSRC   V-RSRC DEP: RES=DATA.SETTLEMENT.EXCLUSIVE
PAYROLL2  4822   RDY    W-RSRC   V-RSRC DEP: RES=DATA.SETTLEMENT.EXCLUSIVE
```
The operations bridge is flooded with escalations, but operators do not know which job holds the lock.""",
        "root_cause": """CA-7 Virtual Resource Management (VRM) controls concurrency using logical resource tokens (Shared `SHR` or Exclusive `EXC`). If an earlier job fails or is purged without signaling de-allocation to the CA-7 queue database, the resource status remains locked at depth 0, blocking all subsequent jobs configured with `EXC` requirements.""",
        "solution": """### 1. Inquire Resource Status via CA-7 Terminal
Query which job holds the lock:
```text
/DISPLAY,ST=RSRC,RES=DATA.SETTLEMENT.EXCLUSIVE
```
Output:
```text
RESOURCE: DATA.SETTLEMENT.EXCLUSIVE  FREE: 0  TOTAL: 1
HELD BY: JOB=LEDGER99 (STATUS: ABENDED SOC7 IN STEP03)
```

### 2. Release Orphaned Lock Manually
Once confirmed that `LEDGER99` is no longer executing on the sysplex:
```text
/FREERSRC,RES=DATA.SETTLEMENT.EXCLUSIVE
```
Within seconds, `PAYROLL1` transitions from `W-RSRC` to `ACT` (Active), and execution resumes!

### 3. Long-Term Architectural Migration: Modern Event-Driven Schedulers
Enterprises migrating away from Broadcom CA-7 eliminate proprietary VRM locks by transitioning to **Stonebranch Universal Automation Center (UAC)** or **BMC Control-M**, which provide:
- RESTful lock orchestration.
- Automated lock timeouts.
- Real-time web visualization dashboards.""",
        "prevention": [
            "Configure automatic lock cleanup on job failure in CA-7 job definition panels.",
            "Audit batch streams to convert unnecessary `EXC` locks to `SHR` where datasets permit.",
            "Establish alert triggers when jobs remain in `W-RSRC` state for over 15 minutes.",
            "Evaluate automated migration paths from CA-7 to Stonebranch or Control-M."
        ],
        "references": [
            {"title": "Broadcom CA-7 Workload Automation: Managing Virtual Resources", "url": "https://techdocs.broadcom.com/us/en/ca-mainframe-software/automation/ca-workload-automation-ca-7-edition.html"},
            {"title": "Stonebranch: Automated CA-7 Migration Architecture", "url": "https://www.stonebranch.com/"},
            {"title": "StackMF Broadcom CA-7 Replacement & Modernization Hub", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },
    {
        "slug": "rexx-interactive-ispf-table-display-utilities",
        "title": "Designing Interactive ISPF Table Displays (TBDISPL) using REXX for Operations Tooling",
        "category": "DevOps & Automation",
        "tags": ["REXX", "ISPF Tables", "TBDISPL", "Panel Design", "Automation", "z/OS"],
        "reading_time": "9 min read",
        "tldr": "Custom operations tooling on z/OS frequently requires scrollable, selectable tables. Discover how to create dynamic ISPF panels, populate in-memory ISPF tables with REXX, and capture user line commands with TBDISPL.",
        "problem": """System programmers and operations analysts spend hours typing repetitive TSO commands to inspect dataset allocations, active locks, and batch logs because no interactive dashboard exists:
```text
TSO LISTCAT ENTRIES('SYS1.PARMLIB') ALL
TSO LISTDS 'PROD.COBOL.LOADLIB'
```
Existing tools either require expensive third-party ISV licenses or clunky batch reports.""",
        "root_cause": """ISPF provides powerful panel table display capabilities via the `TBDISPL` service, but documentation is dense, and developers struggle with row-selection loops, table cursor tracking, and dynamic scrolling variables.""",
        "solution": """### 1. Define the ISPF Panel Definition (MYPANEL)
```text
)ATTR
  _ TYPE(INPUT) INTENS(HIGH) CAPS(ON)
  + TYPE(TEXT) INTENS(LOW)
  # TYPE(OUTPUT) INTENS(LOW)
)BODY
+----------------- STACKMF OPERATIONS DASHBOARD ----------------+
+COMMAND ===>_ZCMD                                              +
+S = SELECT  D = DELETE  B = BROWSE                             +
+CMD  DATASET NAME                               EXTENTS  VOLSER +
)MODEL
 _Z  #DSNAME                                    #EXT    #VOLSER +
)END
```

### 2. REXX Script Driving TBDISPL
```rexx
/* REXX - Interactive ISPF Table Browser */
ADDRESS ISPEXEC

/* 1. Create temporary in-memory table */
"TBCREATE MYSNPT NAMES(DSNAME EXT VOLSER) NOWRITE REPLACE"

/* 2. Populate table rows */
DSNAME = 'PROD.ONLINE.CUSTOMER'; EXT = '03'; VOLSER = 'VOL001'; "TBADD MYSNPT"
DSNAME = 'PROD.ONLINE.ORDERS';   EXT = '01'; VOLSER = 'VOL002'; "TBADD MYSNPT"
DSNAME = 'PROD.BATCH.LEDGER';    EXT = '12'; VOLSER = 'VOL003'; "TBADD MYSNPT"

/* 3. Display table and process user selections */
"TBTOP MYSNPT"
DO FOREVER
  "TBDISPL MYSNPT PANEL(MYPANEL)"
  IF RC >= 8 THEN LEAVE /* User pressed PF3/END */
  
  /* Process selected rows */
  DO WHILE ZTDSELS > 0
    IF Z = 'B' THEN ADDRESS TSO "VIEW DATASET('"DSNAME"')"
    IF Z = 'D' THEN SAY "Confirm delete for: " DSNAME
    IF ZTDSELS > 1 THEN "TBDISPL MYSNPT"
    ELSE ZTDSELS = 0
  END
END

/* 4. Clean up table */
"TBEND MYSNPT"
EXIT 0
```""",
        "prevention": [
            "Always close in-memory tables with `TBEND` in cleanup error traps to avoid storage leaks.",
            "Use `NOWRITE` on temporary tables so ISPTABL dataset libraries are not locked.",
            "Support standard ISPF scroll commands (`PAG`, `CSR`, `MAX`) by binding `ZVERB`.",
            "Migrate frequent queries to Zowe CLI or REST APIs for workstation access."
        ],
        "references": [
            {"title": "IBM z/OS ISPF Dialog Developer's Guide: Table Display Service", "url": "https://www.ibm.com/docs/en/zos/latest?topic=services-tbdispl-display-table-information"},
            {"title": "IBM z/OS TSO/E REXX Reference", "url": "https://www.ibm.com/docs/en/zos/latest?topic=rexx-reference"},
            {"title": "StackMF Mainframe Automation & Tooling Pods", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },
    {
        "slug": "endevor-processor-symbolic-override-troubleshooting",
        "title": "Resolving Endevor Processor Symbolic Override Mismatches during Emergency Bugfixes",
        "category": "DevOps & Automation",
        "tags": ["Broadcom Endevor", "Processors", "Symbolic Overrides", "SCL", "DevOps", "Emergency Fix"],
        "reading_time": "10 min read",
        "tldr": "Broadcom Endevor processor symbolic overrides allow dynamic compiler parameter adjustments, but syntax drifts between stages frequently cause cast failures and missing load modules. Learn how to debug symbolics and migrate smoothly to Git-based CI/CD.",
        "problem": """During an emergency production bugfix, an engineer generates a COBOL element in Broadcom Endevor:
```text
ENDEVOR MESSAGE: C1G0204E SYMBOLIC &CBLOPTS WAS NOT RESOLVED IN PROCESSOR COBCOMP
ENDEVOR MESSAGE: C1X0010E PACKAGE CAST FAILED FOR PACKAGE PKG261001-HOTFIX
```
The overnight maintenance window is slipping away while engineers search through nested processor groups to locate the missing symbol.""",
        "root_cause": """Endevor processors utilize symbolic variables (`&LOADLIB`, `&CBLOPTS`, `&SYSOUT`) evaluated hierarchically:
1. System level definitions.
2. Type level definitions.
3. Processor Group overrides.
4. Element-level overrides in Software Control Language (SCL).
If an element is moved from Stage 1 to Stage 2 where the receiving processor group lacks a corresponding symbol or defines it as non-overridable, the processor fails during packaging.""",
        "solution": """### 1. Inspect Processor Group Symbolics in Endevor
Navigate to Endevor Option 4 (Environments) &rarr; Option 2 (Processor Groups) &rarr; Select `COBCOMP`.
Verify the default values:
```text
SYMBOL       VALUE                              OVERRIDE?
&CBLOPTS     'OPT(2),RENT,APOST,NODYNAM'         Y
&LOADLIB     'PROD.CICS.LOADLIB'                 N
```
If `OVERRIDE?` is set to `N`, element-level overrides will throw `C1G0204E`.

### 2. Supply Valid Symbolic Overrides in SCL
```scl
GENERATE ELEMENT 'ORDR01'
  FROM ENVIRONMENT 'PROD' SYSTEM 'FINANCE' SUBSYSTEM 'BILLING'
       TYPE 'COBOL' STAGE 1
  OPTIONS CCID 'HOTFIX01' COMMENTS 'Emergency fix'
  COPYBACK
  WITH SYMBOLIC &CBLOPTS = 'OPT(0),NOSSRANGE,TEST' .
```

### 3. Replace Fragile Endevor Processors with Git & IBM DBB
Modern enterprises eliminate complex Endevor processors by migrating to **Git** and **IBM Dependency Based Build (DBB)**:
- Build properties are stored as readable JSON / YAML in Git.
- No proprietary SCL syntax.
- Builds run in GitHub Actions or Jenkins with standard Pull Request reviews.""",
        "prevention": [
            "Maintain centralized processor group documentation across all Endevor systems.",
            "Disallow ad-hoc element-level symbolic overrides in production promotion stages.",
            "Run automated package validation prior to scheduled freeze windows.",
            "Evaluate automated Endevor-to-Git migration pipelines using Zowe and DBB."
        ],
        "references": [
            {"title": "Broadcom Endevor Software Control Language (SCL) Reference", "url": "https://techdocs.broadcom.com/us/en/ca-mainframe-software/devops/ca-endevor-software-change-manager.html"},
            {"title": "IBM Dependency Based Build (DBB) for Git DevOps", "url": "https://www.ibm.com/products/dependency-based-build"},
            {"title": "StackMF Broadcom Endevor Replacement with Git Hub", "url": "https://stackmf.com/#broadcom-replacement"}
        ]
    },
    {
        "slug": "changeman-zmf-baseline-reverse-delta-recovery",
        "title": "Recovering Corrupted Mainframe Modules using ChangeMan ZMF Reverse Delta Histories",
        "category": "DevOps & Automation",
        "tags": ["ChangeMan ZMF", "Reverse Delta", "Baseline Recovery", "Audit Trail", "CMN", "Source Control"],
        "reading_time": "9 min read",
        "tldr": "When an unauthorized change or erroneous deployment corrupts a production COBOL baseline, Rocket ChangeMan ZMF reverse deltas provide a forensic recovery path. Learn how to reconstruct historical source revisions and protect baseline integrity.",
        "problem": """A critical batch billing job crashes with unexpected syntax errors:
```text
IGYPS2121-S 'WS-ACC-BAL' WAS NOT DEFINED AS A DATA-NAME
```
Investigation reveals an emergency hotfix overwritten the production baseline without proper regression testing. The team must restore the exact code that was executing at 08:00 AM yesterday.""",
        "root_cause": """ChangeMan ZMF stores historical versions of components in **Reverse Delta** format:
- The current baseline library holds the latest active copy of the source code.
- Historical versions are stored as reverse diffs (deltas) in the CMN delta component libraries.
If engineers attempt manual PDS member copies outside ChangeMan, the delta chain becomes out-of-sync, creating baseline corruption.""",
        "solution": """### 1. View Baseline History in ChangeMan ZMF
Navigate to ChangeMan ZMF Menu Option 1 (Query) &rarr; Option 3 (Baseline):
```text
APPLICATION: FIN1
COMPONENT:   BILL900
TYPE:        COB

REV  PACKAGE     DATE        TIME      USERID    COMMENTS
---  ----------  ----------  --------  --------  -------------------------
 00  FIN1004821  2026/10/05  22:14:02  DEVUSER1  Corrupted emergency patch
-01  FIN1004780  2026/09/20  14:02:11  ARCH01    Verified production baseline
-02  FIN1004650  2026/08/11  09:30:45  DEVUSER2  Prior quarterly release
```

### 2. Extract Previous Revision (-01) into Recovery PDS
Use the `RECOVER` service or batch CMN execution:
```jcl
//RCVRSTEP EXEC PGM=CMNREVRS,
// PARM='FIN1,BILL900,COB,-01'
//STEPLIB  DD DSN=CMN.LOAD,DISP=SHR
//RESTORED DD DSN=TEMP.RECOVERY.COBOL(BILL900),DISP=SHR
```

### 3. Build an Emergency Regression Package
Check out the recovered `-01` baseline into a high-priority ChangeMan package and execute standard compile, promotion, and approval workflows.""",
        "prevention": [
            "Protect production baseline PDS libraries with strict RACF permissions (`READ` for users, `ALTER` only for CMN started tasks).",
            "Never bypass ChangeMan staging libraries during emergency bugfixes.",
            "Audit delta library integrity regularly using `CMNDELCK` utilities.",
            "Consider modern Git-based distributed version control for instantaneous branching and rollbacks."
        ],
        "references": [
            {"title": "Rocket Software ChangeMan ZMF User's Guide", "url": "https://www.rocketsoftware.com/"},
            {"title": "IBM z/OS Security Server RACF Dataset Protection", "url": "https://www.ibm.com/docs/en/zos/latest?topic=racf-protecting-data-sets"},
            {"title": "StackMF Mainframe Modernization & DevOps Transformation", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },
    {
        "slug": "cics-threadsafe-open-transaction-environment-ote",
        "title": "CICS Threadsafe Programming & OTE: Eliminating QR TCB Bottlenecks and Task Switching",
        "category": "CICS & VSAM Architecture",
        "tags": ["CICS TS", "Threadsafe", "OTE", "TCB Switching", "QR TCB", "Open Transaction Environment"],
        "reading_time": "10 min read",
        "tldr": "Transactions bound to the single Quasi-Reentrant (QR) TCB cause throughput plateaus in high-volume CICS regions. Master CICS Open Transaction Environment (OTE), threadsafe COBOL coding standards, and CONCURRENCY(REQUIRED) to execute across concurrent L8/L9 TCBs on multi-core IBM Z processors.",
        "problem": """During peak commercial load, transactions exhibit high dispatch wait times even though general CPU utilization remains below 60%:
```text
DFHAP0001 AN ABEND (CODE ---/AKCS) HAS OCCURRED AT OFFSET X'0000214C'
CICS DISPATCHER SUMMARY: QR TCB CPU DISPATCH RATIO = 99.2% (SATURATED)
AVERAGE TASK WAIT ON DISPATCHER QUEUE: 420MS
```
Transactions queue behind each other on a single core because legacy programs are defined with `CONCURRENCY(QUASIRENT)`.""",
        "root_cause": """CICS originally executed all application code serially on a single task control block: the QR TCB. While DB2 calls execute on open L8 TCBs, every non-threadsafe CICS command causes CICS to switch execution context back to the QR TCB. If a program issues 50 CICS commands interspersed with DB2 queries, it triggers 100 TCB switches, throttling throughput.""",
        "solution": """### 1. Identify Non-Threadsafe CICS Commands
Inspect compile and CICS trace logs. Commands accessing non-shared resources (such as `EXEC CICS RECEIVE`, `READQ`, or legacy terminal I/O) are non-threadsafe and force switches back to the QR TCB.

### 2. Compile COBOL with Threadsafe Options
```jcl
//COMPILE EXEC PGM=IGYCRCTL,
// PARM=('RENT','THREAD','OPT(2)')
```

### 3. Update CSD Program Definition
In the CICS System Definition (CSD):
```text
CEDA ALTER PROGRAM(ORDR01)
  CONCURRENCY(REQUIRED)
  API(CICSAPI)
```
- `CONCURRENCY(REQUIRED)`: CICS dispatches the program immediately onto an open L8/L9 TCB upon entry and remains on open TCBs for all Db2 and threadsafe CICS requests, completely bypassing the QR bottleneck!""",
        "prevention": [
            "Use CICS Performance Analyzer (CICS PA) to measure TCB switch counts per transaction.",
            "Avoid `EXEC CICS ADDRESS CSA` in modern code as it breaks reentrancy.",
            "Utilize CICS Channels and Containers instead of COMMAREA for large payloads.",
            "Convert legacy VSAM files to Record Level Sharing (RLS) to enable threadsafe file I/O."
        ],
        "references": [
            {"title": "IBM CICS TS: Threadsafe Programming Guide", "url": "https://www.ibm.com/docs/en/cics-ts/latest?topic=programming-threadsafe"},
            {"title": "IBM Redbook: CICS and the Open Transaction Environment", "url": "https://www.redbooks.ibm.com/"},
            {"title": "StackMF CICS Core Systems Engineering", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },
    {
        "slug": "db2-bufferpool-tuning-getpage-hit-ratio",
        "title": "Tuning DB2 Buffer Pools (BP0-BP49): Achieving 98%+ Hit Ratios and Reducing Sync Read I/O",
        "category": "DB2 SQL & Performance",
        "tags": ["DB2", "Buffer Pools", "Hit Ratio", "Getpage", "I/O Tuning", "BP0", "z/OS Storage"],
        "reading_time": "9 min read",
        "tldr": "Synchronous DASD reads are the leading cause of transactional latency in DB2 for z/OS. Learn how to calculate buffer pool hit ratios, configure VPSIZE, and tune sequential steal thresholds (VPSEQT) to keep active indexes in memory.",
        "problem": """Application teams report sudden latency spikes on critical online SQL queries:
```text
DSNB401I -DB2P BUFFERPOOL BP1 FULL DISPLAY:
TOTAL GETPAGE OPERATIONS: 45,210,000
SYNCHRONOUS READ I/O:      8,940,000
CALCULATED BUFFER POOL HIT RATIO: 80.2% (TARGET: >= 98%)
AVERAGE SYNC I/O WAIT TIME: 2.4MS PER QUERY
```
High I/O wait times degrade sub-second response SLAs and cause lock contention across the database.""",
        "root_cause": """A low buffer pool hit ratio indicates that DB2 cannot find requested 4KB/8KB/32KB pages in virtual storage, forcing synchronous disk reads. This occurs when:
1. `VPSIZE` is undersized relative to active working set size.
2. Large batch table scans share the same buffer pool as OLTP indexes, flushing cached index pages via aggressive page replacement.""",
        "solution": """### 1. Calculate the Buffer Pool Hit Ratio Formula
```text
HIT_RATIO = (GETPAGE - SYNCHRONOUS_READS) / GETPAGE * 100%
```
For OLTP index pools, the target is 98% to 99.5%.

### 2. Isolate Indexes into Dedicated Buffer Pools
Never mix tables and indexes in BP0. Allocate indexes to a dedicated pool:
```sql
ALTER INDEX DSN8D13A.XEMP1 BUFFERPOOL BP2;
```

### 3. Dynamically Expand Buffer Pool Size Online
Increase virtual pool size without stopping DB2:
```text
-DB2P ALTER BUFFERPOOL(BP2) VPSIZE(250000)
-DB2P ALTER BUFFERPOOL(BP2) VPSEQT(20)
```
- `VPSIZE(250000)`: Allocates 250,000 4KB pages (~1GB of 64-bit storage above the 2GB bar).
- `VPSEQT(20)`: Restricts sequential prefetch to a maximum of 20% of the pool, preventing batch jobs from flushing online transaction cache!""",
        "prevention": [
            "Maintain separate buffer pools for catalog (BP0), tables (BP1), and indexes (BP2/BP3).",
            "Monitor buffer pool paging rates in SMF type 100/102 records.",
            "Use PGFIX(YES) for critical pools to fix pages in real memory and eliminate z/OS page-fix CPU overhead.",
            "Automate buffer pool alerts when synchronous read percentages rise above 5%."
        ],
        "references": [
            {"title": "IBM Db2 13 for z/OS Managing Performance: Tuning Buffer Pools", "url": "https://www.ibm.com/docs/en/db2-for-zos/13?topic=performance-tuning-buffer-pools"},
            {"title": "IBM Redbook: Subsystem and Transaction Monitoring in DB2 for z/OS", "url": "https://www.redbooks.ibm.com/"},
            {"title": "StackMF DB2 SQL & Systems Architecture", "url": "https://stackmf.com/#mainframe-modernization"}
        ]
    },
    {
        "slug": "racf-digital-certificate-expiry-automation",
        "title": "Automating RACF Digital Certificate Renewal and Key Ring Bindings for z/OS HTTPS",
        "category": "DevOps & Automation",
        "tags": ["RACF", "Digital Certificates", "Key Rings", "z/OS Security", "TLS/SSL", "Automation"],
        "reading_time": "10 min read",
        "tldr": "Expired RACF digital certificates bring down z/OSMF REST APIs, Zowe gateways, and CICS web services without warning. Discover how to identify expiring certificates with RACDCERT, automate certificate renewals, and refresh key rings without cycling started tasks.",
        "problem": """At midnight on the 1st of the month, all Zowe CLI and cloud-to-mainframe API integrations fail simultaneously:
```text
ICH408I USER(ZOWEUSER) GROUP(SYS1) NAME(ZOWE DAEMON)
  CERTIFICATE VALIDATION FAILED: CERTIFICATE HAS EXPIRED
CWWKS1106A: Authentication failed for user. SSL handshake error: Certificate expired.
```
Corporate systems cannot communicate with the mainframe, halting digital onboarding and payment portals.""",
        "root_cause": """Internal Certificate Authority (CA) or server certificates stored in the RACF database carry hard expiration dates (typically 1 to 2 years). When a certificate expires:
1. RACF rejects TLS handshakes.
2. Started tasks (z/OSMF, Zowe, CICS, WebSphere Liberty) cache key rings in memory and do not detect changes until the key ring cache is explicitly refreshed.""",
        "solution": """### 1. Audit Expiring Certificates in RACF
Run a batch RACDCERT inquiry to find certificates expiring within 30 days:
```rexx
/* REXX - Audit Expiring RACF Certificates */
ADDRESS TSO
"RACDCERT ID(START1) LIST(LABEL('ZOWECERT'))"
```

### 2. Renew Certificate and Re-Bind to Key Ring
```jcl
//RENEWCRT EXEC PGM=IKJEFT01
//SYSTSPRT DD SYSOUT=*
//SYSTSIN  DD *
  RACDCERT ID(START1) REKEY(LABEL('ZOWECERT')) -
    WITHLABEL('ZOWECERT-2027')
  RACDCERT ID(START1) GENREQ(LABEL('ZOWECERT-2027')) -
    DSN('PROD.CERT.CSR.OUT')
/*
```
Once signed by your corporate PKI:
```text
RACDCERT ID(START1) ADD('PROD.CERT.SIGNED') TRUST
RACDCERT ID(START1) CONNECT(LABEL('ZOWECERT-2027') -
  RING(ZoweKeyring) USAGE(PERSONAL) DEFAULT)
```

### 3. Refresh In-Memory Key Ring Cache Without Recycling Tasks
Signal the z/OS System SSL daemon and Started Tasks to reload key rings immediately:
```text
SETROPTS RACLIST(DIGTCERT, DIGTRING) REFRESH
```
All active HTTPS sessions refresh their TLS credentials with zero system downtime!""",
        "prevention": [
            "Schedule automated weekly REXX audit jobs to scan RACF for certificates expiring in < 60 days.",
            "Integrate RACF certificate lifecycle management with corporate HashiCorp Vault or Venafi via Zowe API.",
            "Document all key ring names and associated started task IDs in enterprise configuration repositories.",
            "Use RACF certificate warning messages (`ICH423I`) to alert operations teams 30 days prior to expiration."
        ],
        "references": [
            {"title": "IBM z/OS Security Server RACF Command Language Reference: RACDCERT", "url": "https://www.ibm.com/docs/en/zos/latest?topic=commands-racdcert-command"},
            {"title": "IBM z/OS Cryptographic Services System SSL Programming", "url": "https://www.ibm.com/docs/en/zos/latest?topic=cryptography-system-ssl"},
            {"title": "StackMF Enterprise Security & Compliance Pods", "url": "https://stackmf.com/#mainframe-developers"}
        ]
    },
    {
        "slug": "mq-channel-status-retrying-resolution",
        "title": "Diagnosing IBM MQ Channel State RETRYING and TCP/IP Heartbeat Timeouts on z/OS",
        "category": "ABENDS & Diagnostics",
        "tags": ["IBM MQ", "MQ for z/OS", "Channels", "RETRYING", "Heartbeat", "TCP/IP Contention"],
        "reading_time": "9 min read",
        "tldr": "IBM MQ Sender and Cluster-Sender channels frequently get stuck in RETRYING state following network drops or firewall idle timeouts. Learn how to diagnose CSQX messages, tune HBINT and DISCINT, and automate channel recovery.",
        "problem": """Messages to payment and fraud detection systems back up in transmission queues (`XMITQ`), causing downstream timeouts:
```text
CSQX500I +MQ1P CSQXRESP Channel TO.AZURE.PAYMENTS started
CSQX548E +MQ1P CSQXRESP Channel TO.AZURE.PAYMENTS failed, connection broken
CSQX501I +MQ1P CSQXRESP Channel TO.AZURE.PAYMENTS is in RETRYING state
```
Current queue depth climbs from 0 to 80,000 messages, threatening transactional buffer limits.""",
        "root_cause": """When an MQ sender channel attempts to transmit a message across TCP/IP, network firewalls frequently drop idle TCP connections without transmitting a `TCP FIN` packet. The z/OS Channel Initiator (CHINIT) remains waiting until the TCP/IP keepalive or MQ heartbeat interval (`HBINT`) expires, placing the channel in `RETRYING` mode.""",
        "solution": """### 1. Inquire Channel Status in MQ Command Console
```text
/cpf DISPLAY CHSTATUS(TO.AZURE.PAYMENTS) ALL
```
Look for `STATUS(RETRYING)`, `SUBSTATE`, and `STOPREQ`.

### 2. Tune Heartbeat (HBINT) and KeepAlive (KAINT) Parameters
Prevent stateful firewall timeouts by configuring active heartbeats:
```text
ALTER CHANNEL(TO.AZURE.PAYMENTS) CHLTYPE(SDR) +
  HBINT(30) +
  KAINT(60) +
  SHRCNV(10) +
  DISCINT(0)
```
- `HBINT(30)`: Sends an in-band MQ heartbeat every 30 seconds when no message traffic is present, keeping firewall connection states alive.
- `DISCINT(0)`: Disables disconnect timeout so channels remain continuously established.

### 3. Force Immediate Channel Restart
To bypass the retry interval timer:
```text
/cpf STOP CHANNEL(TO.AZURE.PAYMENTS) MODE(FORCE)
/cpf START CHANNEL(TO.AZURE.PAYMENTS)
```
The channel re-establishes TCP/IP connection, transitions to `STATUS(RUNNING)`, and drains the transmission queue at thousands of messages per second!""",
        "prevention": [
            "Align MQ `HBINT` with corporate enterprise firewall idle timeout rules (typically 60s or 120s).",
            "Monitor transmission queue depth (`CURDEPTH`) via automated monitoring (Grafana, Instana, Omegamon).",
            "Configure Channel Initiator dispatching priority in WLM to SYSSTC or high priority.",
            "Deploy Dead Letter Queue (DLQ) handlers to prevent corrupt message head-of-line blocking."
        ],
        "references": [
            {"title": "IBM MQ for z/OS Managing Channels: Channel Problems and Diagnostics", "url": "https://www.ibm.com/docs/en/ibm-mq/latest?topic=diagnostics-channel-problems"},
            {"title": "IBM Redbook: High Availability IBM MQ for z/OS Architecture", "url": "https://www.redbooks.ibm.com/"},
            {"title": "StackMF Mainframe Application Support & Maintenance (AMS)", "url": "https://stackmf.com/#maintenance-ams"}
        ]
    },
    {
        "slug": "stonebranch-agent-deployment-zos-automation",
        "title": "Deploying Stonebranch Universal Automation Center Agents on z/OS to Replace CA-7",
        "category": "Modernisation & Cloud",
        "tags": ["Stonebranch", "UAC", "CA-7", "Workload Automation", "z/OS Agent", "Broadcom Replacement"],
        "reading_time": "11 min read",
        "tldr": "Replacing Broadcom CA-7 requires deploying a modern, lightweight workload agent on z/OS that coordinates with cloud orchestrators. Learn step-by-step how to install the Stonebranch Universal Agent, map JCL execution, and achieve a 60% licensing cost reduction.",
        "problem": """Enterprises facing 200%+ price increases on Broadcom CA-7 software renewals seek to migrate to modern workload automation platforms like Stonebranch Universal Automation Center (UAC). However, systems teams fear disruption to thousands of daily z/OS batch production jobs:
```text
AUDIT FINDING: 8,400 ACTIVE CA-7 JOB SCHEDULES AND 14,000 DATASET TRIGGERS
CHALLENGE: How to migrate without a multi-year freeze or operational downtime?
```""",
        "root_cause": """Legacy CA-7 systems bind schedules, dataset triggers (DB.1), and virtual resource locks into proprietary mainframe databases. Modern solutions decouple scheduling orchestration (running in cloud or Linux containers) from execution engines, utilizing lightweight z/OS agents communicating over secure TLS REST/TCP.""",
        "solution": """### 1. Install Stonebranch Universal Agent Started Task on z/OS
Deploy the agent SMP/E or pax file to z/OS UNIX and APF-authorize the load library:
In `SYS1.PROCLIB(UNAGENT)`:
```jcl
//UNAGENT  PROC
//STEP01   EXEC PGM=UNAGENT,REGION=0M,
// PARM='CONFIG=/etc/stonebranch/agent.conf'
//STEPLIB  DD DSN=STONE.AUTM.LOADLIB,DISP=SHR
//SYSPRINT DD SYSOUT=*
//SYSUDUMP DD SYSOUT=*
```

### 2. Configure Agent Communication and Security
In `/etc/stonebranch/agent.conf`:
```properties
CONTROLLER_HOST=uac.enterprise.cloud
CONTROLLER_PORT=7878
SSL_ENABLED=YES
SECURITY_MODEL=RACF
JES_INTERFACE=SUBSYSTEM
```
The agent executes jobs under the submitting user's native RACF / ACF2 / Top Secret credentials, preserving full security auditing!

### 3. Convert CA-7 Schedules to Stonebranch Workflows
Using StackMF's automated conversion parser:
1. Export CA-7 database via `BTI` batch terminal interface.
2. Translate calendar schedules, trigger dependencies, and `VRM` resource locks into Stonebranch JSON workflow definitions.
3. Run parallel dual-run execution for 2 weeks to verify completion return codes (RC=0000).
4. Decommission CA-7 and terminate the license!""",
        "prevention": [
            "Perform automated syntax validation of all converted JCL prior to production cutover.",
            "Run parallel tracking where both schedulers log batch completions to verify timing parity.",
            "Ensure z/OS agent started task is configured in WLM service class `SYSTEM` or `SYSSTC`.",
            "Train operational staff on modern web-based Gantt dashboards to accelerate adoption."
        ],
        "references": [
            {"title": "Stonebranch Universal Automation Center (UAC) Documentation", "url": "https://www.stonebranch.com/universal-automation-center"},
            {"title": "StackMF Broadcom Product Replacement Program & ROI Calculator", "url": "https://stackmf.com/#broadcom-replacement"},
            {"title": "Automating CA-7 Migration to Stonebranch and Control-M Runbook", "url": "https://stackmf.com/blog/automating-ca7-migration-to-stonebranch-controlm.html"}
        ]
    }
]

