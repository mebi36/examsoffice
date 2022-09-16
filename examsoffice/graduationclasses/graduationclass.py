from results.models import Student


class GraduationClass:
    """
    This class models a graduation class: a set of students that share
    the same expected year of graduation. This is the most robust way
    of conceptualizing a class.

    """

    def __init__(self, expected_yr_of_grad: str):
        self.expected_yr_of_grad = expected_yr_of_grad

    @property
    def members(self):
        return list(
            Student.objects.filter(expected_yr_of_grad=self.expected_yr_of_grad)
        )

    def best_student(self):
        """
        This method returns student(s) with the highest CGPA in the class.
        Will return None if class has no members or class members have no
        results in the DB.
        """
        if self.is_empty():
            return None

        valid_members_cgpas = self.members_with_valid_cgpas()

        if len(valid_members_cgpas) == 0:
            return None

        class_highest_cgpa = valid_members_cgpas[
            max(valid_members_cgpas, key=valid_members_cgpas.get)
        ]

        return [
            student
            for (student, cgpa) in valid_members_cgpas.items()
            if cgpa == class_highest_cgpa
        ]

    def ranking(self):
        """
        This method returns a list of class members ordered by their
        current CGPA's.
        """
        members_with_cgpas = self.members_with_valid_cgpas()
        return [
            {k: v}
            for k, v in sorted(
                members_with_cgpas.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        ]

    def members_with_no_results(self):
        """Method return class members with no result on db."""
        return {
            student
            for (student, cgpa) in self.members_cgpas().items()
            if cgpa is None
        }

    def members_cgpas(self):
        class_members = self.members
        return {student: student.current_cgpa() for student in class_members}

    def members_with_valid_cgpas(self):
        class_members_cgpa = self.members_cgpas()
        return {
            student: cgpa
            for (student, cgpa) in class_members_cgpa.items()
            if cgpa is not None
        }

    def is_empty(self):
        return True if len(self.members) == 0 else False

    @property
    def level_of_study(self):
        """returns the class current level of study."""
        raise NotImplementedError()

    level_of_study.setter

    def level_of_study(self, level: int):
        """sets the class's current level of study"""
        raise NotImplementedError()

    def average_cgpa(self):
        """
        This method calculates the classes average CGPA.
        Returns:
        the average CGPA of the class if class members have results in the DB.
        None if the class is empty or class members have no results in the DB.
        """
        if (
            self.is_empty()
            or len(members_and_cgpa := self.members_with_valid_cgpas()) == 0
        ):
            return None

        return round(sum(members_and_cgpa.values()) / len(members_and_cgpa), 3)

    def average_cgpa_per_session(self, session: str):
        """
        This method should take a session and return the average CGPA of
        the class for that academic session, if any results were found
        for the class members in that academic session.
        """
        raise NotImplementedError()

    def student_position(self, student_reg_no: str):
        """
        This method should return a students position in the class when
        students are ranked by CGPAs.
        Will return None if the student does not have any results
        """
        if not Student.is_valid_reg_no(student_reg_no):
            return ValueError("Invalid Student Registration Number")

        student = Student.objects.filter(student_reg_no=student_reg_no)

        if not student.exists():
            return ValueError("No student found with that registration number")

        student = student.first()

        if student.expected_yr_of_grad != self.expected_yr_of_grad:
            return ValueError("Student is not a member of this class")

        student_pos = list(
            filter((lambda x: student in x[1]), enumerate(self.ranking(), 1))
        )

        if len(student_pos) > 0:
            return student_pos[0][0]
        else:
            return None

    def get_class_profile_url(self):
        """
        Returns URL for access the profile page of the class
        """
        raise NotImplementedError()