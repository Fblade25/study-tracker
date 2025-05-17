from PySide6.QtWidgets import QComboBox
from util.util import get_data_path


class SubjectDropdown(QComboBox):
    def __init__(self):
        super().__init__()

    def load_subjects_in_dropdown(self, subject: str = "General") -> None:
        """Reloads subjects in the dropdown menu."""
        parquet_files = [
            file.name for file in get_data_path().iterdir() if file.suffix == ".parquet"
        ]
        self.clear()

        # Load each subject
        for file_name in parquet_files:
            subject_name = file_name.replace(".parquet", "")
            self.addItem(subject_name)

        # Preselect subject
        index = self.findText(subject)
        if index != -1:
            self.setCurrentIndex(index)

    def get_current_subject(self) -> str:
        """Gets the current subject."""
        return self.currentText()
