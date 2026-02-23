from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, BigInteger, UniqueConstraint
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, relationship
import enum
from datetime import datetime

class Base(AsyncAttrs, DeclarativeBase):
    pass

class UserRole(str, enum.Enum):
    TEACHER = 'teacher'
    STUDENT = 'student'


class SubjectEnum(str, enum.Enum):
    PHYSICS = 'Физика'
    MATH = 'Математика'

class DaysEnum(str, enum.Enum):
    MONDAY = 'Понедельник'
    TUESDAY = 'Вторник'
    WEDNESDAY = 'Среда'
    THURSDAY = 'Четверг'
    FRIDAY = 'Пятница'
    SATURDAY = 'Суббота'
    SUNDAY = 'Воскресенье'

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True, nullable=False, index=True)
    name = Column(String(30), nullable=False)
    class_number = Column(Integer, nullable=True)
    role = Column(Enum(UserRole), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())

    lessons_as_student = relationship(
        'Lesson',
        foreign_keys='Lesson.student_id',
        back_populates='student'
    )

    lessons_as_teacher = relationship(
        'Lesson',
        foreign_keys='Lesson.teacher_id',
        back_populates='teacher'
    )

class TeacherStudent(Base):
    __tablename__ = 'teacher_student'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'))
    teacher_id = Column(Integer, ForeignKey('users.id'))
    subject_id = Column(Integer, ForeignKey('subjects.id'))

    __table_args__ = (
        UniqueConstraint('student_id', 'teacher_id', 'subject_id', name='unique_teacher_student_subject'),
    )

class Subject(Base):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True)
    name = Column(Enum(SubjectEnum), unique=True, nullable=False)

    lessons = relationship("Lesson", back_populates='subject')


class UserSubject(Base):
    __tablename__ = 'user_subject'

    id = Column(Integer, primary_key=True) #зачем это мне вообще
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    subject_id = Column(Integer, ForeignKey('subjects.id', ondelete="CASCADE"))

    user = relationship('User', backref='subjects')
    subject = relationship('Subject', backref='users')

class Schedule(Base):
    __tablename__ = 'schedules'

    id = Column(Integer, primary_key=True)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False, index=True)
    day = Column(Enum(DaysEnum), nullable=False)
    time = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    cost = Column(Integer, nullable=False)

class Homework(Base):
    __tablename__ = 'homeworks'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    topics = Column(String(100), nullable=False)
    pdf_file_id = Column(String(200), nullable=False)

    subject = relationship('Subject')
    lesson = relationship('Lesson', back_populates='homework')
    student = relationship('User', foreign_keys=[student_id])
    teacher = relationship('User', foreign_keys=[teacher_id])


class Lesson(Base):
    __tablename__ = 'lessons'

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('users.id'), index=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'))
    teacher_id = Column(Integer, ForeignKey('users.id'))
    topics = Column(String(100), nullable=False)
    homework_id = Column(Integer, ForeignKey('homeworks.id'))

    student = relationship(
        'User',
        foreign_keys=[student_id],
        back_populates='lessons_as_student'
    )

    teacher = relationship(
        'User',
        foreign_keys=[teacher_id],
        back_populates='lessons_as_teacher'
    )

    homework = relationship('Homework', back_populates='lesson')
    subject = relationship('Subject', back_populates='lessons')

    pdf_file_id = Column(String(200), nullable=False)
