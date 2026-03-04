"""add double booking constraint

Revision ID: 07d937f5c0ce
Revises: 43da94d668ed
Create Date: 2026-03-07 21:42:56.552840

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "07d937f5c0ce"
down_revision = "43da94d668ed"
branch_labels = None
depends_on = None


def upgrade():
    """
    Adicionar Restrição EXCLUDE na tabela
    Garante que um médico ou paciente não possua duas consultas
    com horários a menos de 5 minutos de diferença entre si.
    Consultas canceladas são ignoradas pela restrição.
    Fazer a nível do banco de dados, e não do backend, evita problemas de concorrência
    """

    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")

    op.execute("""
        ALTER TABLE appointments
        ADD CONSTRAINT exclude_doctor_appointment_overlap
        EXCLUDE USING gist (
            doctor_id WITH =,
            tsrange(
                scheduled_at,
                scheduled_at + interval '5 minutes'
            ) WITH &&
        )
        WHERE (status != 'CANCELED')
    """)

    op.execute("""
        ALTER TABLE appointments
        ADD CONSTRAINT exclude_patient_appointment_overlap
        EXCLUDE USING gist (
            patient_id WITH =,
            tsrange(
                scheduled_at,
                scheduled_at + interval '5 minutes'
            ) WITH &&
        )
        WHERE (status != 'CANCELED')
    """)


def downgrade():
    op.execute(
        "ALTER TABLE appointments DROP CONSTRAINT exclude_doctor_appointment_overlap"
    )
    op.execute(
        "ALTER TABLE appointments DROP CONSTRAINT exclude_patient_appointment_overlap"
    )
