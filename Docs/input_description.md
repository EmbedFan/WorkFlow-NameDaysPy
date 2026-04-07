# Name Days Monitoring App - Requirements Specification

## Project Overview

This is a **Name Days monitoring application for Windows PCs** that sends notifications for user-selected name day anniversaries and can send automated emails via Gmail.

---

## Core Requirements

### Platform & Technical Stack
- **Implementation Language:** Python
- **Operating System:** Windows only
- **UI Framework:** PyQt5
- **Startup Behavior:**
  - Can be started manually
  - Can be configured to run automatically at Windows startup
- **Resource Usage:** Designed for minimal memory and CPU consumption

### Multilingual Support
- **Default Language:** English
- **Included Languages:** Hungarian
- **Design Principle:** Architecture should allow easy addition of new languages

---

## Notification System

### Notification Frequency & Behavior
- **Check Interval:** Every 15 minutes (**IT IS CONFIGURABLE**)
- **Multiple Names on Same Day:** Each name registered for a single day receives individual notification handling
- **Notification Window:** Displays a modal with three mutually exclusive action buttons

### User Actions on Notification Window

```example_layout
    +-------------------------------------------------------------------------------+
    | Today name days: Tamás                                                        |
    | Important connections with this name:                                         |
    ! Barát Tamás, Róka Tamás (or There is no connections who has this name)        |
    |                                                                               |
    |                                                                               |
    |                                                     [Later]  [Mail]  [Done]   |
    +-------------------------------------------------------------------------------+
```

**In this example, Barát Tamás and Róka Tamás celebrate nameday on the same day!**

1. **`<Later>` Button**
   - Closes the current notification
   - Reschedules notification for this name in **{Notification Frequency}** minutes
   - Returns to background monitoring

2. **`<Mail>` Button**
   - Sends automated email to registered contact (if configured)
   - Requires: automated email feature enabled AND email address(es) registered for the contact
   - On successful send: no further notifications displayed
   - On send failure: remains in notification system

3. **`<Done>` Button**
   - Permanently disables all future notifications for that specific name
   - No recovery without manual database edit

---

## Email Notifications

### Requirements
- **Gmail Integration:** Uses Gmail account for automated email sending
- **Trigger:** Manual click of `<Mail>` button (not fully automatic)
- **Prerequisites:**
  - Automated email feature must be enabled in settings
  - Contact must have one or more registered email addresses
- **Content:** Pre-written, customizable email template per contact
- **Result:** If email sends successfully, no further notifications are shown

---

## User Interface - System Tray Menu

The application provides a system tray icon menu with the following options:

### 1. Edit Notification Database
- Access to manage the list of names to monitor
- Allows adding, removing, modifying contact details

### 2. Show All Names for Current Day
- Displays all names currently registered with namedays today
- Quick reference without separate notifications

### 3. Query Namedays for Name
- Opens dialog window with single line text input
- Buttons: `<Query>` and `<Exit>`
- **On `<Exit>` button:** Close dialog.
- **On `<Query>` button (only if text entered):**
  - If name exists in database: Update the existing record
  - If name does not exist: No nameday registered for this name

### 4. Configure Settings
- **Notification Frequency:** Adjust monitoring interval (default: 15 minutes)
- **Email Settings:** Enable/disable automated email, configure Gmail credentials
- **Language:** Select display language (English, Hungarian, etc.)

### 5. Exit Program
- Cleanly close the application
- Stop background monitoring

---

## Data Model

### Contact Database (User-Managed Records)

#### Data Fields for Contact Record

Each monitored contact record contains:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | Text | Yes | Display name of the contact |
| `main_nameday` | Date (MM-DD) | Yes | Primary nameday date |
| `other_nameday` | Date (MM-DD) | No | Secondary/alternate nameday (optional) |
| `recipient` | Text | Yes | Contact identifier/label |
| `email_addresses` | Text (comma-separated) | No | One or more email addresses |
| `prewritten_email` | Text | No | Custom email template for automated sending |
| `comment` | Text | No | Custom comment for the record |

### CSV Storage Format

```csv
name;main_nameday;other_nameday;recipient;email_addresses;prewritten_email;comment
Tibor;05-12;;Rózsa Tibor;r.tibor156@gmail.com,tibi234@gmail.com;Let me to wish happy namday for you!;My friend
```

### Nameday Reference Database (Built-in)

#### Data Fields for Nameday Reference

| Field | Type | Required | Description |
|-------|------|------|------|
| `name` | Text | Yes | Name |
| `main_nameday` | Text | Yes | Primary date of the nameday |
| `other_nameday` | Text | No | Optional date(s) of the nameday |

### CSV Storage Format

```csv
name;main_nameday;other_nameday
János;06-24;12-27
Mária;08-15;09-12
Andrea;02-04;07-06
Adél;12-24;02-10
```