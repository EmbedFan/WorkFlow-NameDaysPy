Act as a senior software architect and senior developer.

---

## INPUT

System design:

# Name Days Monitoring App - System Design Document

## 1. System Overview

The Name Days Monitoring App is a Windows-exclusive desktop application that monitors contact namedays and delivers timely notifications to users. The system runs in the background, checks at configurable intervals (default 15 minutes) for upcoming namedays, and displays modal notifications with options to defer, send emails, or mark as complete.

**Key Characteristics:**
- Lightweight background service (target: <100MB memory, ~0% CPU idle) [REQ-0024]
- Python-based desktop application using PyQt5 [REQ-0041]
- Windows system tray integration [REQ-0010, REQ-0042]
- Autonomous monitoring with user control [REQ-0022]
- Multi-language support (English, Hungarian) [REQ-0045, REQ-0046]
- Local CSV-based data persistence [REQ-0053]
- Gmail integration for email notifications [REQ-0016, REQ-0052]

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                      Windows Operating System                        │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │                  Name Days Monitoring App                      │ │
│  │                                                                │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │              Application Entry Point                     │ │ │
│  │  │  - Process initialization [REQ-0001]                    │ │ │
│  │  │  - Auto-launch detection [REQ-0002]                     │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  │                           ▲                                    │ │
│  │                           │                                    │ │
│  │  ┌────────────────────────┴──────────────────────────────────┐ │ │
│  │  │          Core Monitoring Engine                          │ │ │
│  │  │  - Background check loop [REQ-0022]                      │ │ │
│  │  │  - Configurable interval [REQ-0003]                      │ │ │
│  │  │  - Thread-based execution                                 │ │ │
│  │  └────┬──────────────────────────────────────────────────────┘ │ │
│  │       │                            │                           │ │
│  │       ▼                            ▼                           │ │
│  │  ┌──────────────────┐    ┌────────────────────┐              │ │
│  │  │ Notification    │    │  System Tray      │              │ │
│  │  │ Manager         │    │  Icon Manager     │              │ │
│  │  │ [REQ-0005,0006..│    │ [REQ-0010, 0042]  │              │ │
│  │  │  0007, 0008]    │    └────────────────────┘              │ │
│  │  └──────────────────┘                                        │ │
│  │       │                                                      │ │
│  │       ▼                                                      │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │        Notification Modal Dialog                        │ │ │
│  │  │  - Display contact info [REQ-0009]                      │ │ │
│  │  │  - Three action buttons [REQ-0044]                      │ │ │
│  │  │  - Modal window focus [REQ-0005]                        │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  │                                                                │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │           UI Components & Dialogs                        │ │ │
│  │  │  - Settings dialog [REQ-0014, 0047]                      │ │ │
│  │  │  - Database editor [REQ-0011, 0049]                      │ │ │
│  │  │  - Query dialog [REQ-0013, 0050]                         │ │ │
│  │  │  - Today's namedays [REQ-0012]                           │ │ │
│  │  └──────────────────────────────────────────────────────────┘ │ │
│  │                           ▲                                    │ │
│  │                           │                                    │ │
│  │  ┌────────────────────────┴──────────────────────────────────┐ │ │
│  │  │          Data Access Layer                              │ │ │
│  │  │  ┌──────────────────────────────────────────────────┐   │ │ │
│  │  │  │ Contact Database Manager [REQ-0017, 0029-0040]  │   │ │ │
│  │  │  │ - CRUD operations                                 │   │ │ │
│  │  │  │ - CSV file I/O                                    │   │ │ │
│  │  │  │ - Data validation                                 │   │ │ │
│  │  │  └──────────────────────────────────────────────────┘   │ │ │
│  │  │  ┌──────────────────────────────────────────────────┐   │ │ │
│  │  │  │ Nameday Reference Manager [REQ-0018, 0038-0039] │   │ │ │
│  │  │  │ - Built-in reference database                    │   │ │ │
│  │  │  │ - Lookup operations                              │   │ │ │
│  │  │  │ - Format: name;main_nameday;other_nameday        │   │ │ │
│  │  │  └──────────────────────────────────────────────────┘   │ │ │
│  │  │  ┌──────────────────────────────────────────────────┐   │ │ │
│  │  │  │ Configuration Manager [REQ-0026, 0055]           │   │ │ │
│  │  │  │ - Settings persistence                           │   │ │ │
│  │  │  │ - Default fallback [REQ-0028]                    │   │ │ │
│  │  │  └──────────────────────────────────────────────────┘   │ │ │
│  │  └────────────────────────────────────────────────────────────┘ │ │
│  │       │                    │                    │               │ │
│  │       ▼                    ▼                    ▼               │ │
│  │  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐       │ │
│  │  │contacts.csv  │   │namedays.csv  │   │config.json   │       │ │
│  │  │[REQ-0037]    │   │[REQ-0039]    │   │[REQ-0055]    │       │ │
│  │  └──────────────┘   └──────────────┘   └──────────────┘       │ │
│  │                                                                │ │
│  │  ┌──────────────────────────────────────────────────────────┐ │ │
│  │  │        Service Integrations                            │ │ │
│  │  │  ┌──────────────────────────────────────────────────┐   │ │ │
│  │  │  │ Email Service [REQ-0016, 0019, 0052]            │   │ │ │
│  │  │  │ - Gmail SMTP/OAuth2 integration                  │   │ │ │
│  │  │  │ - Template support [REQ-0020]                    │   │ │ │
│  │  │  │ - Failure handling [REQ-0027]                    │   │ │ │
│  │  │  └──────────────────────────────────────────────────┘   │ │ │
│  │  │  ┌──────────────────────────────────────────────────┐   │ │ │
│  │  │  │ Windows Integration [REQ-0051]                   │   │ │ │
│  │  │  │ - Startup registry/shortcut configuration        │   │ │ │
│  │  │  │ - Auto-launch management                         │   │ │ │
│  │  │  └──────────────────────────────────────────────────┘   │ │ │
│  │  └────────────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                                                                      │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │  System Tray Integration [REQ-0010, 0042]                     │ │
│  │  - Context menu                                                │ │
│  │  - Quick access to features                                    │ │
│  └────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘

External Systems:
┌──────────────────────────┐
│   Gmail/SMTP Server      │
│  [REQ-0016, REQ-0052]    │
└──────────────────────────┘
         ▲
         │ SMTP/OAuth2
         │
    ┌────┴─────────────────────┐
    │ Email Service Component   │
    └──────────────────────────┘

┌──────────────────────────┐
│  Windows Registry        │
│  [REQ-0002, REQ-0051]    │
└──────────────────────────┘
         ▲
         │ Auto-launch config
         │
    ┌────┴────────────────────────┐
    │ Startup Integration Module   │
    └──────────────────────────────┘
```

---

## 3. Components and Responsibilities

### 3.1 Application Entry Point
**File:** `app/main.py`  
**Responsibilities:**
- Initialize PyQt5 application [REQ-0041]
- Create main application window/tray icon [REQ-0010]
- Start background monitoring thread [REQ-0022]
- Handle application lifecycle (startup, shutdown) [REQ-0001, REQ-0015]
- Detect auto-launch mode [REQ-0002]

**Key Methods:**
- `__init__()` - Initialize application
- `setup_ui()` - Create UI components
- `start_monitoring()` - Start background thread
- `cleanup()` - Graceful shutdown

---

### 3.2 Core Monitoring Engine
**File:** `app/monitoring_engine.py`  
**Responsibilities:**
- Maintain background monitoring loop [REQ-0022]
- Execute periodic checks at configured intervals [REQ-0003]
- Query nameday database for today's namedays [REQ-0018]
- Match against contact database [REQ-0017]
- Trigger notifications for matches [REQ-0004]
- Handle rescheduling via "Later" button [REQ-0006]
- Resource-efficient implementation [REQ-0024]

**Key Methods:**
- `start()` - Begin monitoring loop
- `stop()` - Stop monitoring gracefully
- `check_namedays()` - Query and match namedays
- `queue_notification()` - Add notification to queue
- `set_interval()` - Update check interval [REQ-0003]

**Threading:** Runs in background thread to prevent UI blocking

---

### 3.3 Notification Manager
**File:** `app/notification_manager.py`  
**Responsibilities:**
- Manage notification queue [REQ-0004]
- Display notification modal [REQ-0005]
- Handle notification window focus [REQ-0005]
- Process button actions (Later, Mail, Done) [REQ-0006, 0007, 0008]
- Track notification state (displayed, actioned)
- Support multiple namedays on same day [REQ-0004]

**Key Methods:**
- `show_notification()` - Display modal
- `handle_later()` - Reschedule notification [REQ-0006]
- `handle_mail()` - Trigger email sending [REQ-0007]
- `handle_done()` - Permanently disable notifications [REQ-0008]
- `queue_notifications()` - Batch multiple notifications

---

### 3.4 Notification Modal Dialog
**File:** `app/ui/notification_modal.py`  
**Responsibilities:**
- Display contact nameday information [REQ-0009]
- Show "Important connections" list [REQ-0009]
- Render three action buttons [REQ-0044]
- Maintain modal focus and blocking behavior [REQ-0005]
- Display contact name clearly [REQ-0009]

**Layout Components:**
```
┌─────────────────────────────────┐
│  Today name days: [Name]        │
│                                 │
│  Important connections with     │
│  this name:                     │
│  - [Connection 1]               │
│  - [Connection 2]               │
│                                 │
│                    [Later][Mail][Done]
└─────────────────────────────────┘
```

**Requirements:** [REQ-0043, REQ-0044]

---

### 3.5 System Tray Manager
**File:** `app/ui/system_tray.py`  
**Responsibilities:**
- Create and manage system tray icon [REQ-0010, REQ-0042]
- Provide context menu [REQ-0010]
- Handle menu actions (minimize, show, exit) [REQ-0015]
- Respond to tray icon clicks
- Update icon state (active, inactive)

**Context Menu Items:**
- Show All Names Today [REQ-0012]
- Query Nameday [REQ-0013]
- Settings [REQ-0014]
- Edit Notification Database [REQ-0011]
- Exit [REQ-0015]

---

### 3.6 Settings Manager
**File:** `app/managers/settings_manager.py`  
**Responsibilities:**
- Load settings from configuration file [REQ-0026]
- Save settings on modification [REQ-0026]
- Provide default settings [REQ-0028]
- Handle corrupted configuration gracefully [REQ-0028]
- Support settings: interval, email config, language [REQ-0026]
- Notify components of setting changes

**Key Methods:**
- `load_settings()` - From disk [REQ-0026]
- `save_settings()` - To disk
- `get_setting()` - Retrieve setting value
- `set_setting()` - Update setting
- `reset_to_defaults()` - Recovery [REQ-0028]

**Settings Schema:**
```json
{
  "check_interval": 15,
  "auto_launch": false,
  "language": "en",
  "email_provider": "gmail",
  "gmail_email": "",
  "gmail_password": "",
  "notifications_enabled": true
}
```

---

### 3.7 Contact Database Manager
**File:** `app/managers/contact_db_manager.py`  
**Responsibilities:**
- Implement CRUD operations [REQ-0017]
- Handle CSV file I/O with semicolon delimiter [REQ-0037]
- Validate contact data before storage [REQ-0040]
- Persist changes [REQ-0021]
- Manage contact fields [REQ-0029]
- Enforce required fields [REQ-0040]

**Contact Record Structure:** [REQ-0029]
```csv
name;main_nameday;other_nameday;recipient;email_addresses;prewritten_email;comment
János;06-04;11-30;János Péter;janos@example.com;Dear János, Happy nameday!;Friend
```

**Field Validation:** [REQ-0040]
- `name` - Required, non-empty text [REQ-0030]
- `main_nameday` - Required, MM-DD format [REQ-0031, REQ-0023]
- `other_nameday` - Optional, MM-DD format [REQ-0032, REQ-0023]
- `recipient` - Required, non-empty text [REQ-0033]
- `email_addresses` - Optional, comma-separated [REQ-0034]
- `prewritten_email` - Optional, text [REQ-0035]
- `comment` - Optional, free text [REQ-0036]

**Key Methods:**
- `create_contact()` - Add new contact
- `read_contacts()` - Load all contacts
- `update_contact()` - Modify contact
- `delete_contact()` - Remove contact
- `validate_contact()` - Check data [REQ-0040]
- `get_contact_by_name()` - Lookup
- `export_csv()` - Write to file

---

### 3.8 Nameday Reference Manager
**File:** `app/managers/nameday_reference_manager.py`  
**Responsibilities:**
- Maintain built-in nameday reference database [REQ-0018]
- Support Hungarian and other names [REQ-0018]
- Provide lookup operations [REQ-0018]
- Load reference CSV [REQ-0039]
- Support name search [REQ-0013]

**Nameday Reference Structure:** [REQ-0038, REQ-0039]
```csv
name;main_nameday;other_nameday
János;06-04;11-30
Mária;05-01;08-15
Andrea;11-30;06-22
Adél;12-24;
```

**Minimum Required Names:** János, Mária, Andrea, Adél [REQ-0018]

**Key Methods:**
- `get_nameday()` - Lookup by name [REQ-0013]
- `get_all_names()` - List all available names
- `search_names()` - Find names with pattern
- `get_names_for_date()` - Get names for MM-DD [REQ-0023]
- `load_reference()` - Initialize from CSV

---

### 3.9 Email Service
**File:** `app/services/email_service.py`  
**Responsibilities:**
- Send emails via Gmail SMTP/OAuth2 [REQ-0016, REQ-0052]
- Support prewritten templates [REQ-0020]
- Handle email failures gracefully [REQ-0027]
- Validate email addresses [REQ-0040]
- Send only on explicit user action [REQ-0019]
- Support multiple recipients [REQ-0034]

**Key Methods:**
- `send_email()` - Send via SMTP [REQ-0007]
- `validate_email()` - Check format [REQ-0040]
- `authenticate()` - Gmail auth [REQ-0052]
- `apply_template()` - Use prewritten template [REQ-0020]

**Email Flow:** [REQ-0019]
- Only triggered by Mail button click [REQ-0007]
- Never automatic [REQ-0019]
- Disables further notifications on success [REQ-0007]

---

### 3.10 Windows Startup Integration
**File:** `app/services/windows_startup.py`  
**Responsibilities:**
- Configure Windows startup registry/shortcut [REQ-0051]
- Enable/disable auto-launch [REQ-0002]
- Detect if running at startup [REQ-0002]
- Handle Windows 10/11 compatibility [REQ-0025]

**Key Methods:**
- `enable_auto_launch()` - Add to startup [REQ-0002]
- `disable_auto_launch()` - Remove from startup
- `is_auto_launch_enabled()` - Check status [REQ-0002]
- `is_running_at_startup()` - Detect startup mode [REQ-0002]

---

### 3.11 UI Components - Settings Dialog
**File:** `app/ui/settings_dialog.py`  
**Responsibilities:**
- Display settings interface [REQ-0014, REQ-0047]
- Provide input fields for all settings [REQ-0047]
- Language selection dropdown [REQ-0045]
- Apply changes on save, discard on cancel [REQ-0047]
- Update UI immediately on language change [REQ-0045]

**Modal Structure:** [REQ-0047]
- Check interval input
- Auto-launch checkbox [REQ-0002]
- Language selection [REQ-0045]
- Gmail credentials inputs [REQ-0016]
- Save/Cancel buttons

---

### 3.12 UI Components - Database Editor
**File:** `app/ui/database_editor.py`  
**Responsibilities:**
- Provide contact management interface [REQ-0011, REQ-0049]
- Support add/edit/delete operations [REQ-0011, REQ-0049]
- Show visual feedback [REQ-0049]
- Display data validation messages [REQ-0049]
- Allow user to modify contact database [REQ-0011]

**Features:**
- Add contact form [REQ-0011]
- Edit contact form [REQ-0011]
- Delete contact with confirmation [REQ-0011]
- List all contacts [REQ-0011]
- Search contacts [REQ-0011]

---

### 3.13 UI Components - Query Dialog
**File:** `app/ui/query_dialog.py`  
**Responsibilities:**
- Display nameday search dialog [REQ-0013]
- Accept name input [REQ-0013, REQ-0050]
- Implement Query/Exit buttons [REQ-0050]
- Display search results [REQ-0050]
- Handle case sensitivity per language [REQ-0013]

**Modal Structure:** [REQ-0050]
- Text input field
- Query button
- Exit button
- Results display area

---

### 3.14 UI Components - Today's Namedays View
**File:** `app/ui/today_namedays_view.py`  
**Responsibilities:**
- Display all today's namedays [REQ-0012]
- Show complete contact list [REQ-0012]
- Update in real-time [REQ-0012]
- Provide quick reference [REQ-0012]

---

### 3.15 Internationalization (i18n) Manager
**File:** `app/i18n/i18n_manager.py`  
**Responsibilities:**
- Manage multilingual strings [REQ-0046]
- Support English (default) and Hungarian [REQ-0045]
- Allow easy addition of new languages [REQ-0046]
- Externalize all UI strings [REQ-0046]

**Structure:**
```
app/i18n/
  en.json - English strings
  hu.json - Hungarian strings
  i18n_manager.py - Translation engine
```

---

## 4. Data Flow

### 4.1 Startup Flow
```
1. Application starts [REQ-0001]
   ↓
2. Check if running at Windows startup [REQ-0002]
   ↓
3. Initialize settings from config file [REQ-0026]
   ├─ If corrupted, use defaults [REQ-0028]
   └─ If missing, create defaults [REQ-0028]
   ↓
4. Load language [REQ-0046]
   ↓
5. Initialize UI [REQ-0041]
   ├─ Create system tray icon [REQ-0010]
   └─ Create main window (hidden if startup) [REQ-0002]
   ↓
6. Load contact database from CSV [REQ-0017, REQ-0021]
   ├─ Validate contact data [REQ-0040]
   └─ Handle errors gracefully [REQ-0027]
   ↓
7. Load nameday reference database [REQ-0018, REQ-0039]
   ↓
8. Start background monitoring thread [REQ-0022]
   └─ Set check interval [REQ-0003]
   ↓
9. Ready for notifications
```

---

### 4.2 Monitoring Check Loop
```
Every [configured interval] minutes [REQ-0003]:

1. Execute check_namedays()
   ↓
2. Get current date (MM-DD format) [REQ-0023]
   ↓
3. Query nameday reference database
   └─ Find all names with today's date [REQ-0018]
   ↓
4. For each matching name:
   ├─ Query contact database [REQ-0017]
   ├─ Find all contacts with that nameday [REQ-0004]
   ├─ Check if notifications disabled for contact [REQ-0008]
   ├─ Skip if already notified this session
   └─ Queue notification [REQ-0004]
   ↓
5. For each queued notification:
   └─ Display modal [REQ-0005]
   
6. Reschedule next check at interval [REQ-0003]
```

---

### 4.3 Notification Interaction Flow

#### Later Button [REQ-0006]
```
User clicks "Later"
   ↓
1. Close notification modal [REQ-0005]
   ↓
2. Reschedule for next check interval [REQ-0006]
   ├─ Add to deferred queue
   └─ Don't show until next interval [REQ-0006]
   ↓
3. Return to background monitoring [REQ-0022]
```

#### Mail Button [REQ-0007, REQ-0019]
```
Mail button clicked
   ↓
1. Check if enabled (contact has email) [REQ-0007]
   ├─ If no email, stay disabled
   └─ If email exists, enable button [REQ-0007]
   ↓
2. Send email via Gmail SMTP [REQ-0016, REQ-0052]
   ├─ Load prewritten template if exists [REQ-0020]
   ├─ Send to configured email addresses [REQ-0034]
   └─ Handle failures gracefully [REQ-0027]
   ↓
3. On success:
   ├─ Disable future notifications [REQ-0007]
   └─ Close modal [REQ-0005]
   ↓
4. On failure:
   └─ Show error message, keep modal open
```

#### Done Button [REQ-0008]
```
User clicks "Done"
   ↓
1. Show warning about irreversibility [REQ-0008]
   ├─ "This action cannot be undone"
   └─ "Manual database edit required" [REQ-0008]
   ↓
2. Update contact database:
   ├─ Set notification_disabled flag [REQ-0008]
   └─ Persist to CSV [REQ-0017]
   ↓
3. Close modal [REQ-0005]
   ↓
4. Skip future notifications for this name [REQ-0008]
```

---

### 4.4 Settings Update Flow
```
User opens Settings Dialog [REQ-0014]
   ↓
1. Load current settings [REQ-0026]
   ↓
2. Display in form [REQ-0047]
   ├─ Current interval [REQ-0003]
   ├─ Auto-launch status [REQ-0002]
   ├─ Language selection [REQ-0045]
   └─ Email settings [REQ-0016]
   ↓
3. User modifies settings
   ↓
4. User clicks Save [REQ-0047]
   ├─ Validate inputs
   ├─ Apply settings [REQ-0047]
   └─ Persist to config file [REQ-0026]
   ↓
5. Notify monitoring engine:
   ├─ Update interval if changed [REQ-0003]
   ├─ Update language if changed [REQ-0045]
   └─ Apply without restart [REQ-0003]
   ↓
6. On cancel:
   └─ Discard changes [REQ-0047]
```

---

### 4.5 Database CRUD Flow

#### Create Contact [REQ-0017]
```
Add Contact Form
   ↓
1. User fills contact fields [REQ-0030-0036]
   ↓
2. Validate data [REQ-0040]
   ├─ Name non-empty [REQ-0030]
   ├─ Main nameday MM-DD [REQ-0031]
   ├─ Other nameday MM-DD or empty [REQ-0032]
   ├─ Recipient non-empty [REQ-0033]
   ├─ Email format valid [REQ-0034]
   └─ All required fields present [REQ-0040]
   ↓
3. On validation success:
   ├─ Add to contact database
   ├─ Write to contacts.csv [REQ-0037]
   └─ Show success message [REQ-0049]
   ↓
4. On validation failure:
   └─ Display validation errors [REQ-0049]
```

#### Read Contacts [REQ-0017]
```
Load contact database
   ↓
1. Open contacts.csv [REQ-0037]
   ├─ UTF-8 encoding [REQ-0037]
   └─ Semicolon delimiter [REQ-0037]
   ↓
2. Parse header row [REQ-0037]
   ↓
3. For each data row:
   ├─ Convert to contact object [REQ-0029]
   └─ Validate data [REQ-0040]
   ↓
4. Return contact list
```

#### Update Contact [REQ-0017]
```
Edit Contact Form
   ↓
1. Load contact data [REQ-0017]
   ↓
2. User modifies fields [REQ-0030-0036]
   ↓
3. Validate modified data [REQ-0040]
   ↓
4. On success:
   ├─ Update contact object
   ├─ Rewrite contacts.csv [REQ-0037]
   └─ Show success message [REQ-0049]
   ↓
5. On failure:
   └─ Display validation errors
```

#### Delete Contact [REQ-0017]
```
Delete Contact
   ↓
1. Show confirmation dialog [REQ-0049]
   ↓
2. User confirms delete
   ↓
3. Remove from contact database
   ↓
4. Rewrite contacts.csv [REQ-0037]
   ↓
5. Show success message [REQ-0049]
```

---

## 5. Storage Design

### 5.1 Contact Database (contacts.csv)
**Location:** `<app_data_dir>/contacts.csv`  
**Format:** UTF-8 encoded, semicolon-delimited [REQ-0037]  
**Headers:** `name;main_nameday;other_nameday;recipient;email_addresses;prewritten_email;comment` [REQ-0037]

**Example:**
```csv
name;main_nameday;other_nameday;recipient;email_addresses;prewritten_email;comment
János;06-04;11-30;János Péter;janos@example.com;Dear János,\nHappy nameday!;Friend from work
Mária;05-01;08-15;Mária Kiss;;Dear Mária,\nWishing you a wonderful day!;Manager
Andrea;11-30;06-22;Andrea Nagy;andrea1@example.com;andrea2@example.com;;Doctor
Adél;12-24;;Adél Szépségszalon;;Direct to salon;;Closes early on nameday
```

**Requirements:**
- Semicolon delimiter [REQ-0037]
- UTF-8 encoding [REQ-0037]
- Headers in first row [REQ-0037]
- Minimal fields validation [REQ-0040]
- Data integrity maintained [REQ-0017]
- Persist across sessions [REQ-0021]

---

### 5.2 Nameday Reference Database (namedays.csv)
**Location:** `<app_data_dir>/namedays.csv` (bundled with application)  
**Format:** UTF-8 encoded, semicolon-delimited [REQ-0039]  
**Headers:** `name;main_nameday;other_nameday` [REQ-0039]

**Example:**
```csv
name;main_nameday;other_nameday
János;06-04;11-30
Mária;05-01;08-15
Andrea;11-30;06-22
Adél;12-24;
```

**Requirements:**
- Semicolon delimiter [REQ-0039]
- UTF-8 encoding [REQ-0039]
- Headers in first row [REQ-0039]
- Built-in reference [REQ-0018]
- Minimum 4 names (János, Mária, Andrea, Adél) [REQ-0018]
- Extensible for additional names [REQ-0018]
- MM-DD date format [REQ-0023]

---

### 5.3 Configuration File (config.json)
**Location:** `<app_data_dir>/config.json`  
**Format:** JSON  
**Persistence:** Across sessions [REQ-0026]  
**Recovery:** Defaults if corrupted [REQ-0028]

**Schema:**
```json
{
  "check_interval": 15,
  "auto_launch": false,
  "language": "en",
  "gmail_account": "",
  "gmail_password": "",
  "notifications_enabled": true,
  "theme": "default"
}
```

**Requirements:**
- Persist settings [REQ-0026]
- All configurable settings included [REQ-0026]
- Load on startup [REQ-0026]
- Default fallback if missing [REQ-0028]
- Graceful handling if corrupted [REQ-0028]

---

### 5.4 Windows Registry (Auto-Launch)
**Location:** `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run` [REQ-0051]  
**Key:** `NameDaysMonitoringApp`  
**Value:** Path to application executable [REQ-0051]

**Requirements:**
- Registry-based configuration [REQ-0051]
- Windows 10/11 compatible [REQ-0025]
- Enable/disable via settings [REQ-0002]
- Persistent after reboot [REQ-0002]

---

### 5.5 Application Data Directory Structure
```
%APPDATA%/NameDaysMonitoringApp/
├── contacts.csv              [REQ-0037]
├── config.json               [REQ-0055]
├── logs/
│   └── app.log (optional)
└── cache/ (optional)
    └── namedays_cache.db
```

**Note:** namedays.csv bundled with application in `resources/`

---

## 6. API Definitions

### 6.1 Core Monitoring Engine API

#### `MonitoringEngine` Class

```python
class MonitoringEngine:
    """Background monitoring for namedays."""
    
    def start(self) -> None:
        """
        Start background monitoring loop.
        Requirement: REQ-0022
        """
        
    def stop(self) -> None:
        """
        Stop monitoring gracefully.
        Requirement: REQ-0022
        """
        
    def check_namedays(self) -> List[Notification]:
        """
        Query databases and find today's namedays.
        
        Returns:
            List of Notification objects for each match.
            
        Requirements: REQ-0018, REQ-0023, REQ-0017
        """
        
    def set_interval(self, minutes: int) -> None:
        """
        Update check interval.
        
        Args:
            minutes: Check interval in minutes
            
        Requirements: REQ-0003
        Note: Changes apply without restart per REQ-0003
        """
        
    def queue_notification(self, notification: Notification) -> None:
        """
        Add notification to queue.
        
        Requirements: REQ-0004, REQ-0022
        """
```

---

### 6.2 Notification Manager API

#### `NotificationManager` Class

```python
class NotificationManager:
    """Manage notification display and user actions."""
    
    def show_notification(self, notification: Notification) -> None:
        """
        Display notification modal.
        
        Args:
            notification: Notification object with contact info
            
        Requirements: REQ-0005, REQ-0043, REQ-0044
        Note: Modal is focused and blocking per REQ-0005
        """
        
    def handle_later(self, notification: Notification) -> None:
        """
        Reschedule notification for next interval.
        
        Args:
            notification: Notification to reschedule
            
        Requirements: REQ-0006
        Note: Closes modal and returns to background
        """
        
    def handle_mail(self, contact: Contact) -> bool:
        """
        Send email to contact.
        
        Args:
            contact: Contact object to email
            
        Returns:
            True if sent successfully, False otherwise
            
        Requirements: REQ-0007, REQ-0019, REQ-0020
        Note: Only triggered by explicit user action per REQ-0019
        """
        
    def handle_done(self, contact: Contact) -> None:
        """
        Permanently disable notifications for contact.
        
        Args:
            contact: Contact to disable notifications
            
        Requirements: REQ-0008
        Note: Irreversible, updates database with warning
        """
```

---

### 6.3 Settings Manager API

#### `SettingsManager` Class

```python
class SettingsManager:
    """Manage application settings."""
    
    def load_settings(self) -> Dict[str, Any]:
        """
        Load settings from config file.
        
        Returns:
            Dictionary of settings
            
        Requirements: REQ-0026, REQ-0028
        """
        
    def save_settings(self, settings: Dict[str, Any]) -> None:
        """
        Save settings to config file.
        
        Args:
            settings: Settings dictionary
            
        Requirements: REQ-0026
        """
        
    def get_setting(self, key: str) -> Any:
        """
        Get individual setting value.
        
        Args:
            key: Setting key
            
        Returns:
            Setting value
            
        Requirements: REQ-0026
        """
        
    def set_setting(self, key: str, value: Any) -> None:
        """
        Update individual setting.
        
        Args:
            key: Setting key
            value: New value
            
        Requirements: REQ-0026
        """
        
    def reset_to_defaults(self) -> None:
        """
        Reset all settings to defaults.
        
        Requirements: REQ-0028
        """
```

---

### 6.4 Contact Database Manager API

#### `ContactDatabaseManager` Class

```python
class ContactDatabaseManager:
    """CRUD operations for contact database."""
    
    def create_contact(self, contact: Contact) -> None:
        """
        Add new contact to database.
        
        Args:
            contact: Contact object with validated fields
            
        Requirements: REQ-0017, REQ-0040
        """
        
    def read_contacts(self) -> List[Contact]:
        """
        Load all contacts from CSV.
        
        Returns:
            List of Contact objects
            
        Requirements: REQ-0017, REQ-0021, REQ-0040
        """
        
    def update_contact(self, contact_id: str, updated: Contact) -> None:
        """
        Update existing contact.
        
        Args:
            contact_id: Contact identifier
            updated: Updated Contact object
            
        Requirements: REQ-0017, REQ-0040
        """
        
    def delete_contact(self, contact_id: str) -> None:
        """
        Delete contact from database.
        
        Args:
            contact_id: Contact identifier to delete
            
        Requirements: REQ-0017
        """
        
    def get_contact_by_name(self, name: str) -> Optional[Contact]:
        """
        Find contact by name.
        
        Args:
            name: Contact name to search
            
        Returns:
            Contact object or None if not found
            
        Requirements: REQ-0017
        """
        
    def get_contacts_by_nameday(self, date: str) -> List[Contact]:
        """
        Find all contacts with given nameday.
        
        Args:
            date: Nameday in MM-DD format
            
        Returns:
            List of matching Contact objects
            
        Requirements: REQ-0023, REQ-0017
        """
        
    def validate_contact(self, contact: Contact) -> List[str]:
        """
        Validate contact data.
        
        Args:
            contact: Contact object to validate
            
        Returns:
            List of validation errors (empty if valid)
            
        Requirements: REQ-0040
        """
```

---

### 6.5 Nameday Reference Manager API

#### `NamedayReferenceManager` Class

```python
class NamedayReferenceManager:
    """Query and manage nameday reference database."""
    
    def get_nameday(self, name: str) -> Optional[Nameday]:
        """
        Lookup nameday by name.
        
        Args:
            name: Name to search (case handling per language)
            
        Returns:
            Nameday object with main/other dates or None
            
        Requirements: REQ-0013, REQ-0018, REQ-0023
        """
        
    def get_names_for_date(self, date: str) -> List[str]:
        """
        Find all names with given nameday date.
        
        Args:
            date: Date in MM-DD format
            
        Returns:
            List of name strings
            
        Requirements: REQ-0018, REQ-0023
        """
        
    def get_all_names(self) -> List[str]:
        """
        Get all available names in reference.
        
        Returns:
            List of all name strings
            
        Requirements: REQ-0018
        """
        
    def search_names(self, pattern: str) -> List[str]:
        """
        Search names by pattern.
        
        Args:
            pattern: Search pattern
            
        Returns:
            List of matching names
            
        Requirements: REQ-0013
        """
```

---

### 6.6 Email Service API

#### `EmailService` Class

```python
class EmailService:
    """Send emails via Gmail integration."""
    
    def send_email(self, to_addresses: List[str], 
                   subject: str, body: str, 
                   template: Optional[str] = None) -> bool:
        """
        Send email to recipients.
        
        Args:
            to_addresses: List of recipient email addresses
            subject: Email subject
            body: Email body text
            template: Optional prewritten template to use
            
        Returns:
            True if sent successfully, False otherwise
            
        Requirements: REQ-0007, REQ-0016, REQ-0019, REQ-0020
        Note: Only called on explicit Mail button click
        """
        
    def authenticate(self, email: str, password: str) -> bool:
        """
        Authenticate with Gmail account.
        
        Args:
            email: Gmail email address
            password: Gmail password or app-specific password
            
        Returns:
            True if authenticated successfully
            
        Requirements: REQ-0016, REQ-0052
        """
        
    def validate_email(self, email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid format
            
        Requirements: REQ-0040, REQ-0034
        """
```

---

### 6.7 Windows Startup Integration API

#### `WindowsStartupManager` Class

```python
class WindowsStartupManager:
    """Manage Windows startup integration."""
    
    def enable_auto_launch(self) -> bool:
        """
        Register application for auto-launch at startup.
        
        Returns:
            True if successfully registered
            
        Requirements: REQ-0002, REQ-0051
        Note: Persists across reboots per REQ-0002
        """
        
    def disable_auto_launch(self) -> bool:
        """
        Unregister application from auto-launch.
        
        Returns:
            True if successfully unregistered
            
        Requirements: REQ-0002, REQ-0051
        """
        
    def is_auto_launch_enabled(self) -> bool:
        """
        Check if auto-launch is currently enabled.
        
        Returns:
            True if enabled
            
        Requirements: REQ-0002
        """
        
    def is_running_at_startup(self) -> bool:
        """
        Detect if application started at system startup.
        
        Returns:
            True if started by Windows at boot
            
        Requirements: REQ-0002
        """
```

---

### 6.8 Internationalization API

#### `I18nManager` Class

```python
class I18nManager:
    """Manage multilingual strings."""
    
    def set_language(self, language: str) -> None:
        """
        Set active language.
        
        Args:
            language: Language code (e.g., 'en', 'hu')
            
        Requirements: REQ-0045, REQ-0046
        Note: Updates UI immediately per REQ-0045
        """
        
    def get_string(self, key: str) -> str:
        """
        Get translated string by key.
        
        Args:
            key: String identifier
            
        Returns:
            Translated string in current language
            
        Requirements: REQ-0046
        """
        
    def get_available_languages(self) -> List[str]:
        """
        Get list of available languages.
        
        Returns:
            List of language codes
            
        Requirements: REQ-0045, REQ-0046
        """
```

---

## 7. External Integrations

### 7.1 Gmail SMTP Integration [REQ-0016, REQ-0052]
**Purpose:** Send notification emails to configured contacts  
**Credentials:** Email address + password (or app-specific password)  
**Authentication:** SMTP via Gmail servers  
**Failure Handling:** Graceful error messages [REQ-0027]  
**Security:** Credentials stored in config file, enable password masking [REQ-0026]

**Integration Points:**
- Email Service class [Section 6.6]
- Settings Manager for credential persistence [Section 6.3]
- Notification Manager triggers on Mail button [Section 6.2]

**Error Scenarios:**
- Invalid credentials: Show error dialog, allow retry
- Network unavailable: Queue for retry
- Rate limit exceeded: Graceful backoff messaging
- Recipient email invalid: Validation at save time [REQ-0040]

---

### 7.2 Windows Auto-Launch Integration [REQ-0002, REQ-0051]
**Purpose:** Register application for auto-start with Windows  
**Method:** Windows Registry entry  
**Location:** `HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run`  
**Compatibility:** Windows 10/11 [REQ-0025]

**Integration Points:**
- Windows Startup Manager class [Section 6.7]
- Settings Dialog for enable/disable [Section 3.11]
- Application startup detection [Section 3.1]

**Behavior:**
- On enable: Create registry key pointing to executable
- On disable: Remove registry key
- On startup: Detect and run minimized to tray [REQ-0002]
- Persist across reboots [REQ-0002]

---

### 7.3 Windows System Tray Integration [REQ-0010, REQ-0042]
**Purpose:** Integrate with Windows notification/system tray area  
**API:** PyQt5 QSystemTrayIcon [REQ-0041]  
**Menu:** Context menu with application options  
**Icon:** Visual indicator in system tray

**Integration Points:**
- System Tray Manager class [Section 3.5]
- UI initialization [Section 3.1]

**Context Menu:**
- Show All Names Today [REQ-0012]
- Query Nameday [REQ-0013]
- Settings [REQ-0014]
- Edit Database [REQ-0011]
- Exit [REQ-0015]

---

## 8. Non-Functional Design Considerations

### 8.1 Resource Efficiency [REQ-0024]
- **Memory Target:** < 100MB footprint
- **CPU Target:** ~0% when idle
- **Strategy:**
  - Async/background thread for monitoring [REQ-0022]
  - Minimal UI when minimized to tray
  - Efficient CSV parsing (not loading entire file repeatedly)
  - Configurable check intervals [REQ-0003]

### 8.2 Error Handling & Recovery [REQ-0027, REQ-0028]
- **Email Failures:** Fail gracefully with user message [REQ-0027]
- **Config Corruption:** Fall back to defaults [REQ-0028]
- **CSV Parsing Errors:** Skip malformed records, log warning
- **Missing Files:** Generate defaults [REQ-0028]
- **Network Errors:** Queue for retry where applicable

### 8.3 Data Integrity [REQ-0040, REQ-0021]
- **Validation:** All input validated before storage [REQ-0040]
- **Persistence:** Changes immediately saved to CSV [REQ-0021]
- **Backup:** Consider transaction pattern for CSV writes
- **Encoding:** UTF-8 consistently [REQ-0037, REQ-0039]

### 8.4 Windows Platform Requirements [REQ-0025]
- **Target OS:** Windows 10/11 only [REQ-0025]
- **Python Version:** 3.7+ for compatibility
- **Dependencies:** PyQt5, Windows-specific modules as needed
- **No macOS/Linux:** All Windows-specific APIs used appropriately [REQ-0025]

### 8.5 Scalability Considerations
- **Contact Database:** Designed for hundreds of contacts (CSV limitation ~10k rows)
- **Nameday Reference:** Built-in database extensible for additional names [REQ-0018]
- **Memory:** Held in memory during runtime, minimal persistence I/O
- **Notification Queue:** Single-threaded queue processing

---

## 9. Deployment & Release

### 9.1 Application Distribution
- **Installer:** Windows executable (.exe) with PyInstaller
- **Auto-Update:** Optional update check mechanism
- **Configuration:** Auto-created on first run
- **Data Directory:** %APPDATA%/NameDaysMonitoringApp/

### 9.2 Database Files
- **Bundled:** namedays.csv with application
- **User Data:** contacts.csv and config.json created on first run
- **Backup:** Consider export functionality in database editor

### 9.3 Release Checklist
- [ ] All 55 requirements traced and implemented
- [ ] All UI strings externalized [REQ-0046]
- [ ] Memory profiling completed [REQ-0024]
- [ ] Windows 10/11 tested [REQ-0025]
- [ ] Email functionality verified with test account [REQ-0016]
- [ ] Auto-launch registry configuration tested [REQ-0051]
- [ ] CSV parsing with various edge cases [REQ-0040]
- [ ] Error messages user-friendly [REQ-0027]

---

## 10. Traceability Matrix

### High-Priority Requirements Coverage
| REQ ID | Component | Status |
|--------|-----------|--------|
| REQ-0001 | Application Entry Point | Core |
| REQ-0002 | Windows Startup Integration | Windows Startup Manager |
| REQ-0003 | Notification Check Interval | Monitoring Engine |
| REQ-0004 | Multiple Names Same Day | Monitoring Engine |
| REQ-0005 | Notification Modal Display | Notification Modal Dialog |
| REQ-0006 | Later Button Functionality | Notification Manager |
| REQ-0007 | Mail Button Functionality | Notification Manager, Email Service |
| REQ-0008 | Done Button Functionality | Notification Manager |
| REQ-0009 | Notification Window Layout | Notification Modal Dialog |
| REQ-0010 | System Tray Icon | System Tray Manager |
| REQ-0011 | Edit Notification Database | Database Editor UI |
| REQ-0014 | Configure Settings | Settings Manager, Settings Dialog |
| REQ-0015 | Exit Application | Application Entry Point |
| REQ-0016 | Gmail Integration | Email Service |
| REQ-0017 | Contact Database CRUD | Contact Database Manager |
| REQ-0018 | Nameday Reference Database | Nameday Reference Manager |
| REQ-0019 | Email Sending Trigger | Email Service (explicit user action) |
| REQ-0021 | Contact Record Persistence | Contact Database Manager |
| REQ-0022 | Background Monitoring | Monitoring Engine |
| REQ-0023 | Nameday Date Format | Contact/Nameday Managers |
| REQ-0024 | Minimal Resource Usage | Architecture/Threading Design |
| REQ-0025 | Windows Platform Only | Windows Startup Manager |
| REQ-0026 | Configuration Persistence | Settings Manager |
| REQ-0027 | Graceful Error Handling | All Services |
| REQ-0028 | Settings Recovery | Settings Manager |
| REQ-0029 | Contact Record Fields | Contact Database Manager |
| REQ-0030-0036 | Contact Record Field Details | Contact Database Manager |
| REQ-0037 | Contact CSV File Format | Contact Database Manager |
| REQ-0038-0040 | Data Validation | All Data Managers |
| REQ-0041 | PyQt5 Framework | UI Framework |
| REQ-0042 | System Tray Integration | System Tray Manager |
| REQ-0043-0044 | Notification Modal Layout | Notification Modal Dialog |
| REQ-0045-0046 | Multilingual UI Support | I18n Manager |
| REQ-0047 | Settings Dialog Interface | Settings Dialog UI |
| REQ-0049 | Database Editor Interface | Database Editor UI |
| REQ-0050 | Query Dialog Interface | Query Dialog UI |
| REQ-0051 | Windows Startup Integration | Windows Startup Manager |
| REQ-0052 | Gmail SMTP Integration | Email Service |
| REQ-0053 | CSV File Integration | Database Managers |
| REQ-0054 | Windows Notifications API | Optional Enhancement |
| REQ-0055 | Configuration File Storage | Settings Manager |

---

## Document Control
**Version:** 1.0  
**Date:** 2026-03-30  
**Status:** Final Design  
**Aligned With:** Requirements Document v1.0 (55 requirements)

---

## TASK

Generate an implementation plan.

---

## INCLUDE

- Module breakdown
- File structure
- Class and function definitions
- Technology stack
- Step-by-step implementation plan
- Mapping to REQ IDs

---

## CONSTRAINTS

- Use Python
- Use snake_case naming
- Include inline documentation expectations

---

## OUTPUT

- Markdown
- Structured
- Ready for coding phase

Save as: /docs/implementation.md