# Workflow: How Applications Get Archived

## Overview
Applications in the loan credit system move through several statuses, with "Архив" (Archive) being the final status for completed or rejected applications.

## Application Status Lifecycle

### Initial Status
- **Новая** (New) - Application is freshly created and not yet reviewed

### Processing Statuses
- **На рассмотрении** (Under Review) - Application is being processed
- **Одобрена** (Approved) - Application has been approved
- **Отклонена** (Rejected) - Application has been rejected

### Final Status
- **Архив** (Archive) - Application has completed processing (either approved or rejected)

## How Applications Move to Archive

### Method 1: Reject Action (Most Common)
1. Employee opens an application by clicking "Обработать заявку" (Process Application)
2. Employee acquires an exclusive lock on the application (10-minute timeout)
3. Employee clicks "✗ Отклонить заявку" (Reject Application) button
4. The application status is automatically moved to "Архив" (Archive)
5. The lock is released

**Backend Implementation:**
- Route: `POST /api/applications/{id}/reject`
- Status Change: Application status → `STATUS_ARCHIVED` (Архив)
- API Response: Returns updated application with new status

### Method 2: Approve Action (Alternative)
1. Employee processes application and approves it
2. Application status changes to "Одобрена" (Approved)
3. Application remains visible but is marked as processed
4. (Optional: Future enhancement could auto-archive approved applications after time period)

## Filtering Archived Applications

### UI Filter Buttons
The Applications table includes filter buttons to view different application groups:

- **Все заявки** (All) - Shows all applications regardless of status
- **Открытые** (Open) - Shows only "Новая" (New) and "На рассмотрении" (Under Review)
- **Закрытые** (Closed) - Shows "Одобрена" (Approved) and "Отклонена" (Rejected) applications
- **Архив** (Archive) - Shows only "Архив" (Archive) status applications

### Example Filter Implementation
```javascript
const isOpen = status === 'Новая' || status === 'На рассмотрении';
const isClosed = status === 'Одобрена' || status === 'Отклонена';
const isArchived = status === 'Архив';
```

## Key Points

1. **Automatic Archival**: When you click "Отклонить заявку" (Reject Application), the system automatically moves it to Archive status.

2. **Archive Filter**: Use the "Архив" filter button to see only archived applications.

3. **Lock Timeout**: If you acquire a lock on an application (10-minute limit) but don't process it within that time, the lock expires and another employee can process it.

4. **Status Immutability**: Once an application reaches Archive status, it cannot be reopened or re-processed through the UI. This prevents accidental re-processing of completed applications.

5. **Data Preservation**: Archived applications are never deleted—all historical data is preserved for audit purposes.

## Technical Details

### Database
- Applications are stored in the `credit_applications` table
- Status is stored in the `status` column with values: 'Новая', 'На рассмотрении', 'Одобрена', 'Отклонена', 'Архив'
- Locks are managed in the `application_locks` table with a 10-minute `timeout_at` timestamp

### API Endpoints
- **GET /api/applications** - List all applications
- **POST /api/applications/{id}/lock** - Acquire lock for editing
- **DELETE /api/applications/{id}/lock** - Release lock
- **POST /api/applications/{id}/reject** - Reject application (moves to Archive)
- **POST /api/applications/{id}/approve** - Approve application

## FAQ

**Q: Can I un-archive an application?**
A: No, archiving is final. This is by design to prevent accidental modifications to completed applications.

**Q: What happens to a lock when I reject an application?**
A: The lock is automatically released when the application moves to Archive status, allowing the table view to update correctly.

**Q: How long does an application stay in Archive?**
A: Indefinitely. Archived applications are never deleted—they remain in the system for historical record-keeping and audit trails.

**Q: Can multiple employees see archived applications?**
A: Yes, all employees with access to the system can view archived applications in the "Архив" filter view, but they cannot modify them.
