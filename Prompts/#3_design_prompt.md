Act as a senior software architect.

---

## INPUT

Requirements document:

# Name Days Monitoring App - Requirements Document

## Functional Requirements

| ID | Title | Description | Priority | Acceptance Criteria | Dependencies | Notes |
|---|---|---|---|---|---|---|
| REQ-0001 | Manual Application Start | Application can be started manually by the user | High | User can launch the application from command line or Windows shortcut | None | Windows only |
| REQ-0002 | Windows Startup Auto-Launch | Application can be configured to run automatically at Windows startup | High | Setting exists to enable/disable auto-launch; when enabled, app starts with system | REQ-0024 | Configuration persists after reboot |
| REQ-0003 | Notification Check Interval | Application monitors for namedays at configurable intervals with default of 15 minutes | High | Default interval is 15 minutes; user can modify interval in settings; system respects configured interval | REQ-0024 | Interval changes apply without restart |
| REQ-0004 | Multiple Names Same Day Notification | Each name on a single nameday receives individual notification handling | High | When multiple contacts have nameday on same day, each receives separate notification; user can action each independently | REQ-0009 | Example: Tamás and János on same day = 2 notifications |
| REQ-0005 | Notification Modal Display | Notification appears as modal window showing nameday information | High | Modal window displays: name, "Important connections" list, three action buttons; modal is focused and blocking | None | Modal layout specified in design |
| REQ-0006 | Later Button Functionality | "Later" button reschedules notification for current interval duration | High | Clicking "Later" closes notification; reschedules for next check interval; returns to background | REQ-0003 | No further notifications until next interval |
| REQ-0007 | Mail Button Functionality | "Mail" button sends automated email to registered contact | High | Button only enabled if contact has email addresses; sends email on click; disables further notifications on success | REQ-0016, REQ-0020 | Fails gracefully if email send fails |
| REQ-0008 | Done Button Functionality | "Done" button permanently disables all future notifications for that specific name | High | Clicking "Done" disables notifications permanently; no recovery without manual database edit; user is clearly warned | None | Irreversible action |
| REQ-0009 | Notification Window Layout | Notification displays contact name and associated "Important connections" | High | Shows "Today name days: [name]"; lists associated contacts; displays fallback if no connections | None | CSV format used internally |
| REQ-0010 | System Tray Icon | Application provides system tray icon with menu | High | Icon visible in system tray; clicking provides context menu with options | None | Windows system tray |
| REQ-0011 | Edit Notification Database | Menu option allows user to manage contact database | High | Menu option "Edit Notification Database" available; opens database editor; allows add/remove/modify | REQ-0017 | CSV file based |
| REQ-0012 | Show All Names for Current Day | Menu option displays all registered names with namedays today | Medium | Menu option available; displays complete list of today's namedays; updates in real-time | REQ-0017 | Quick reference feature |
| REQ-0013 | Query Namedays for Name | Menu option opens dialog to search for specific nameday | Medium | Dialog with text input; "Query" and "Exit" buttons; displays nameday if found; message if not found | REQ-0018 | Case handling defined per language |
| REQ-0014 | Configure Settings | Menu option provides access to all configurable settings | High | Opens settings dialog; allows modification of notification frequency, email settings, language | REQ-0024 | Settings persist across sessions |
| REQ-0015 | Exit Application | Menu option cleanly closes the application | High | "Exit" option in menu; cleanly stops all background monitoring; saves state | None | Graceful shutdown |
| REQ-0016 | Gmail Integration | Application can send emails via Gmail account | High | Uses Gmail API or SMTP; sends to configured email addresses; handles failures gracefully | REQ-0024 | Requires Gmail credentials in settings |
| REQ-0017 | Contact Database CRUD | Application supports Create, Read, Update, Delete operations on contact records | High | All CRUD operations work; changes persisted to CSV; data integrity maintained | None | Semi-colon delimiter |
| REQ-0018 | Nameday Reference Database | Built-in reference database of nameday dates for common names | High | Contains at minimum: János, Mária, Andrea, Adél with dates; can be extended; used for lookups | None | Hungarian and other names included |
| REQ-0019 | Email Sending Trigger | Email only sent on explicit "Mail" button click, not automatic | High | Email never sends without user action; only sends when Mail button clicked | REQ-0007 | User has full control |
| REQ-0020 | Prewritten Email Template | Each contact can have custom email template for notifications | Medium | Template stored in database; used when Mail button clicked; customizable per contact | REQ-0017 | Optional field |
| REQ-0021 | Contact Record Persistence | Contact information persists across application sessions | High | All contact data saved to CSV file; loaded on startup; no data loss on app restart | REQ-0017 | CSV format specified |
| REQ-0022 | Background Monitoring | Application monitors for namedays while running in background | High | Monitoring continues even when notification closed; no user interaction required to maintain monitoring | REQ-0003, REQ-0005 | Resource efficient |
| REQ-0023 | Nameday Date Format | Nameday dates stored and processed in MM-DD format | High | All dates use MM-DD format (e.g., "06-24"); no year component; consistent across app | None | Allows recurring annual notifications |

## Non-Functional Requirements

| ID | Title | Description | Priority | Acceptance Criteria | Dependencies | Notes |
|---|---|---|---|---|---|---|
| REQ-0024 | Minimal Resource Usage | Application designed for minimal memory and CPU consumption | High | Memory footprint under 100MB; CPU usage near 0% when idle; efficiently checks at 15-minute intervals | None | Windows resource constraints |
| REQ-0025 | Windows Platform Only | Application runs exclusively on Windows | High | No dependencies on macOS or Linux; uses Windows-specific APIs appropriately; tested on Windows 10/11 | None | Windows operating system requirement |
| REQ-0026 | Configuration Persistence | All user settings persist across application sessions | High | Settings saved to configuration file; loaded on startup; changes take effect appropriately | None | Settings include interval, email config, language |
| REQ-0027 | Graceful Error Handling | Application handles errors without crashing | Medium | Invalid data handled gracefully; email failures don't crash app; missing files managed appropriately | None | User-friendly error messages |
| REQ-0028 | Settings Recovery | Application functions with default settings if configuration corrupted | Medium | Default values applied if config unreadable; user can reset to defaults manually | None | Prevents startup failures |

## Data Requirements

| ID | Title | Description | Priority | Acceptance Criteria | Dependencies | Notes |
|---|---|---|---|---|---|---|
| REQ-0029 | Contact Record Fields | Contact records contain specified data fields | High | Records include: name, main_nameday, other_nameday, recipient, email_addresses, prewritten_email, comment; required fields enforced | None | Semicolon-delimited CSV |
| REQ-0030 | Contact Name Field | Contact must have display name | High | Name field required; non-empty; stored and displayed correctly | None | Text format |
| REQ-0031 | Primary Nameday Field | Contact must have primary nameday date | High | main_nameday required; MM-DD format; validated for valid dates | None | Annual recurring date |
| REQ-0032 | Secondary Nameday Field | Contact can have optional secondary nameday | Medium | other_nameday optional; MM-DD format if provided; null/empty if not used | None | Some names have multiple dates |
| REQ-0033 | Recipient Identifier Field | Contact must have recipient identifier/label | High | recipient field required; non-empty; distinguishes contact (e.g., "Rózsa Tibor") | None | User-defined label |
| REQ-0034 | Email Addresses Field | Contact can have multiple email addresses | Medium | Comma-separated list supported; at least one email for Mail functionality; validated format | None | Optional field |
| REQ-0035 | Prewritten Email Field | Contact can have custom email template | Medium | Text field; supports any template content; used when sending mail; optional | None | Per-contact customization |
| REQ-0036 | Comment Field | Contact can have optional comment | Low | Free-text field; no length restriction; supports any user notes | None | User reference |
| REQ-0037 | Contact CSV File Format | Contact database stored in CSV with semicolon delimiter | High | File extension .csv; semicolon-delimited; UTF-8 encoding; headers in first row | None | Example: name;main_nameday;other_nameday;recipient;email_addresses;prewritten_email;comment |
| REQ-0038 | Nameday Reference Field Structure | Reference database contains name, main_nameday, other_nameday | High | name: text; main_nameday: MM-DD; other_nameday: MM-DD or empty | None | Built-in reference |
| REQ-0039 | Nameday Reference CSV Format | Nameday reference stored in CSV with semicolon delimiter | High | File extension .csv; semicolon-delimited; UTF-8 encoding; headers in first row | None | Example: name;main_nameday;other_nameday |
| REQ-0040 | Data Validation | All input data validated before storage | High | MM-DD dates validated; email addresses validated; required fields enforced; malformed records rejected | None | Prevents data corruption |

## UI/UX Requirements

| ID | Title | Description | Priority | Acceptance Criteria | Dependencies | Notes |
|---|---|---|---|---|---|---|
| REQ-0041 | PyQt5 Framework | UI built with PyQt5 framework | High | All UI components use PyQt5; cross-platform rendering; compatible with Windows | None | Python UI framework |
| REQ-0042 | System Tray Integration | Application integrates with Windows system tray | High | Icon visible in tray; right-click context menu available; minimize to tray supported | None | Native Windows feature |
| REQ-0043 | Notification Modal Layout | Notification displays in specified layout format | High | Shows: "Today name days: [name]"; "Important connections with this name:"; contact list; three buttons aligned right | None | See design specification |
| REQ-0044 | Modal Button Arrangement | Three buttons arranged horizontally and mutually exclusive | High | Buttons: [Later] [Mail] [Done]; positioned at bottom right; only one action per click | None | User chooses one action |
| REQ-0045 | Language Selection Interface | Settings provide language selection dropdown | High | Available languages visible; switching languages updates UI immediately; default is English | REQ-0046 | Hungarian included |
| REQ-0046 | Multilingual UI Support | Application UI displays in selected language | High | English available (default); Hungarian available; easy to add new languages; strings externalized | None | Architecture supports i18n |
| REQ-0047 | Settings Dialog Interface | Settings dialog modal with input fields and save/cancel buttons | High | Displays all configurable settings; changes applied on save; cancelled changes discarded | None | Modal window |
| REQ-0048 | Notification Dismissal | Notification can be dismissed by application reload or timeout | Medium | User can close notification via buttons; notification auto-closes after configurable duration if needed | None | User-driven primarily |
| REQ-0049 | Database Editor Interface | Database editor provides intuitive contact management | Medium | Add, edit, delete operations available; visual feedback for actions; data validation shown | REQ-0011 | User-friendly form |
| REQ-0050 | Query Dialog Interface | Query dialog has text input and action buttons | High | Text input field for name search; "Query" button triggers search; "Exit" button closes; clear results display | REQ-0013 | Modal dialog |

## Integration Requirements

| ID | Title | Description | Priority | Acceptance Criteria | Dependencies | Notes |
|---|---|---|---|---|---|---|
| REQ-0051 | Windows Startup Integration | Application integrates with Windows startup mechanisms | High | Registry or shortcut configured for auto-start; can be enabled/disabled via settings; tested on Windows 10/11 | REQ-0002 | Windows-specific |
| REQ-0052 | Gmail SMTP Integration | Application uses Gmail SMTP or OAuth2 for email sending | High | Connects to Gmail servers; authenticates with provided credentials; sends emails successfully; handles auth failures | REQ-0016 | Gmail API or SMTP |
| REQ-0053 | CSV File Integration | Application reads/writes CSV files for data persistence | High | CSV files created/updated correctly; semicolon delimiter used; UTF-8 encoding maintained; concurrent access handled | None | Data storage mechanism |
| REQ-0054 | Windows Notifications API | Application can use Windows notification/toast integration if applicable | Low | Optional use of Windows notification APIs; falls back to custom modal if unavailable | None | Enhancement possibility |
| REQ-0055 | Configuration File Storage | Application stores settings in configuration file/database | High | Settings persisted to file; loaded on startup; location appropriate for Windows user config standards | None | Could be INI, JSON, or registry |

## Summary Statistics

- **Total Requirements:** 55
- **High Priority:** 42
- **Medium Priority:** 11
- **Low Priority:** 2
- **Categories:**
  - Functional: 23
  - Non-Functional: 5
  - Data: 12
  - UI/UX: 10
  - Integration: 5
---

## TASK

Generate a system design document.

---

## INCLUDE

- System overview
- Architecture diagram (textual)
- Components and responsibilities
- Data flow
- Storage design
- API definitions
- External integrations

---

## CONSTRAINTS

- Align strictly with requirements
- No new features
- Maintain traceability (reference REQ IDs)

---

## OUTPUT

- Markdown
- Structured sections
- No explanations outside document

Save as: /docs/system_design.md