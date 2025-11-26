"""
Employee repository for database operations.
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from ..models import Employee, OnboardingChecklist, IDPhoto, AccountCredentials
from ..utils.database import get_db
from ..utils.exceptions import DatabaseError, log_error, log_info

class EmployeeRepository:
    """Repository for employee-related database operations."""

    def __init__(self, db: Session):
        """Initialize repository with database session."""
        self.db = db

    def create_employee(self, first_name: str, last_name: str) -> Employee:
        """
        Create a new employee.

        Args:
            first_name: Employee's first name
            last_name: Employee's last name

        Returns:
            Created employee object
        """
        try:
            employee = Employee(
                first_name=first_name,
                last_name=last_name
            )
            self.db.add(employee)
            self.db.commit()
            self.db.refresh(employee)

            # Create associated onboarding checklist
            checklist = OnboardingChecklist(employee_id=employee.id)
            self.db.add(checklist)
            self.db.commit()

            log_info(f"Created employee {employee.id}")
            return employee

        except Exception as e:
            self.db.rollback()
            log_error(e, "Failed to create employee")
            raise DatabaseError(f"Failed to create employee: {str(e)}")

    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """
        Get employee by ID.

        Args:
            employee_id: Employee ID

        Returns:
            Employee object or None if not found
        """
        try:
            return self.db.query(Employee).filter(Employee.id == employee_id).first()
        except Exception as e:
            log_error(e, f"Failed to get employee {employee_id}")
            raise DatabaseError(f"Failed to get employee: {str(e)}")

    def update_employee(self, employee_id: str, **kwargs) -> Optional[Employee]:
        """
        Update employee information.

        Args:
            employee_id: Employee ID
            **kwargs: Fields to update

        Returns:
            Updated employee object or None if not found
        """
        try:
            employee = self.get_employee(employee_id)
            if employee:
                for key, value in kwargs.items():
                    if hasattr(employee, key):
                        setattr(employee, key, value)
                self.db.commit()
                self.db.refresh(employee)
                log_info(f"Updated employee {employee_id}")
            return employee
        except Exception as e:
            self.db.rollback()
            log_error(e, f"Failed to update employee {employee_id}")
            raise DatabaseError(f"Failed to update employee: {str(e)}")

    def get_onboarding_checklist(self, employee_id: str) -> Optional[OnboardingChecklist]:
        """
        Get onboarding checklist for employee.

        Args:
            employee_id: Employee ID

        Returns:
            Onboarding checklist or None if not found
        """
        try:
            return self.db.query(OnboardingChecklist).filter(
                OnboardingChecklist.employee_id == employee_id
            ).first()
        except Exception as e:
            log_error(e, f"Failed to get checklist for employee {employee_id}")
            raise DatabaseError(f"Failed to get checklist: {str(e)}")

    def update_onboarding_checklist(self, employee_id: str, **kwargs) -> Optional[OnboardingChecklist]:
        """
        Update onboarding checklist.

        Args:
            employee_id: Employee ID
            **kwargs: Fields to update

        Returns:
            Updated checklist or None if not found
        """
        try:
            checklist = self.get_onboarding_checklist(employee_id)
            if checklist:
                for key, value in kwargs.items():
                    if hasattr(checklist, key):
                        setattr(checklist, key, value)
                self.db.commit()
                self.db.refresh(checklist)
                log_info(f"Updated checklist for employee {employee_id}")
            return checklist
        except Exception as e:
            self.db.rollback()
            log_error(e, f"Failed to update checklist for employee {employee_id}")
            raise DatabaseError(f"Failed to update checklist: {str(e)}")

    def create_id_photo(self, employee_id: str, file_path: str) -> IDPhoto:
        """
        Create ID photo record.

        Args:
            employee_id: Employee ID
            file_path: Path to ID photo file

        Returns:
            Created ID photo object
        """
        try:
            id_photo = IDPhoto(
                employee_id=employee_id,
                file_path=file_path
            )
            self.db.add(id_photo)
            self.db.commit()
            self.db.refresh(id_photo)
            log_info(f"Created ID photo for employee {employee_id}")
            return id_photo
        except Exception as e:
            self.db.rollback()
            log_error(e, f"Failed to create ID photo for employee {employee_id}")
            raise DatabaseError(f"Failed to create ID photo: {str(e)}")

    def get_id_photo(self, employee_id: str) -> Optional[IDPhoto]:
        """
        Get ID photo for employee.

        Args:
            employee_id: Employee ID

        Returns:
            ID photo object or None if not found
        """
        try:
            return self.db.query(IDPhoto).filter(IDPhoto.employee_id == employee_id).first()
        except Exception as e:
            log_error(e, f"Failed to get ID photo for employee {employee_id}")
            raise DatabaseError(f"Failed to get ID photo: {str(e)}")

    def update_id_photo_status(self, employee_id: str, status: str, notes: Optional[str] = None) -> Optional[IDPhoto]:
        """
        Update ID photo verification status.

        Args:
            employee_id: Employee ID
            status: Verification status
            notes: Optional verification notes

        Returns:
            Updated ID photo object or None if not found
        """
        try:
            id_photo = self.get_id_photo(employee_id)
            if id_photo:
                id_photo.verification_status = status
                if notes:
                    id_photo.verification_notes = notes
                self.db.commit()
                self.db.refresh(id_photo)
                log_info(f"Updated ID photo status for employee {employee_id}")
            return id_photo
        except Exception as e:
            self.db.rollback()
            log_error(e, f"Failed to update ID photo status for employee {employee_id}")
            raise DatabaseError(f"Failed to update ID photo status: {str(e)}")

    def create_account_credentials(self, employee_id: str, account_type: str, username: str) -> AccountCredentials:
        """
        Create account credentials record.

        Args:
            employee_id: Employee ID
            account_type: Type of account (email, git)
            username: Assigned username

        Returns:
            Created account credentials object
        """
        try:
            credentials = AccountCredentials(
                employee_id=employee_id,
                account_type=account_type,
                username=username
            )
            self.db.add(credentials)
            self.db.commit()
            self.db.refresh(credentials)
            log_info(f"Created {account_type} credentials for employee {employee_id}")
            return credentials
        except Exception as e:
            self.db.rollback()
            log_error(e, f"Failed to create {account_type} credentials for employee {employee_id}")
            raise DatabaseError(f"Failed to create credentials: {str(e)}")

    def get_account_credentials(self, employee_id: str, account_type: str) -> Optional[AccountCredentials]:
        """
        Get account credentials for employee.

        Args:
            employee_id: Employee ID
            account_type: Type of account (email, git)

        Returns:
            Account credentials object or None if not found
        """
        try:
            return self.db.query(AccountCredentials).filter(
                AccountCredentials.employee_id == employee_id,
                AccountCredentials.account_type == account_type
            ).first()
        except Exception as e:
            log_error(e, f"Failed to get {account_type} credentials for employee {employee_id}")
            raise DatabaseError(f"Failed to get credentials: {str(e)}")

    def get_all_employees(self) -> List[Employee]:
        """
        Get all employees.

        Returns:
            List of all employees
        """
        try:
            return self.db.query(Employee).all()
        except Exception as e:
            log_error(e, "Failed to get all employees")
            raise DatabaseError(f"Failed to get employees: {str(e)}")

# Global repository factory function
def get_employee_repository(db: Session) -> EmployeeRepository:
    """Factory function to get employee repository."""
    return EmployeeRepository(db)