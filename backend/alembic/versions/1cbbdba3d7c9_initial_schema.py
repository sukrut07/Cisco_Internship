"""initial_schema

Revision ID: 1cbbdba3d7c9
Revises: 
Create Date: 2026-08-30 00:50:19.382931

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1cbbdba3d7c9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'cases',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.String(length=50), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('symptom', sa.Text(), nullable=False),
        sa.Column('topology', sa.Text(), nullable=False),
        sa.Column('show_outputs', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('expected_fault', sa.Text(), nullable=True),
        sa.Column('expected_osi_layer', sa.String(length=50), nullable=True),
        sa.Column('concept', sa.String(length=100), nullable=True),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='MEDIUM'),
        sa.Column('expected_fix', sa.Text(), nullable=True, server_default='[]'),
        sa.Column('next_command', sa.String(length=255), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True, server_default='[]'),
        sa.Column('workflow_state', sa.String(length=50), nullable=False, server_default='CREATED'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('case_id')
    )
    op.create_index('ix_cases_case_id', 'cases', ['case_id'], unique=True)
    op.create_index('ix_cases_category', 'cases', ['category'], unique=False)
    op.create_index('ix_cases_concept', 'cases', ['concept'], unique=False)
    op.create_index('ix_cases_severity', 'cases', ['severity'], unique=False)
    op.create_index('ix_cases_category_severity', 'cases', ['category', 'severity'], unique=False)
    op.create_index('ix_cases_created_at', 'cases', ['created_at'], unique=False)

    op.create_table(
        'diagnoses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.String(length=50), nullable=False),
        sa.Column('root_cause', sa.Text(), nullable=False),
        sa.Column('confidence', sa.String(length=10), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('evidence', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('osi_layer', sa.String(length=50), nullable=True),
        sa.Column('concept', sa.String(length=100), nullable=True),
        sa.Column('next_command', sa.String(length=255), nullable=True),
        sa.Column('fix_steps', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('limitations', sa.Text(), nullable=True, server_default='[]'),
        sa.Column('ai_provider', sa.String(length=50), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=True),
        sa.Column('prompt_version', sa.String(length=50), nullable=True),
        sa.Column('raw_response', sa.Text(), nullable=True),
        sa.Column('grounding_status', sa.String(length=30), nullable=False, server_default='UNKNOWN'),
        sa.Column('confidence_signals', sa.Text(), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.case_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_diagnoses_case_id', 'diagnoses', ['case_id'], unique=False)
    op.create_index('ix_diagnoses_case_id_created', 'diagnoses', ['case_id', 'created_at'], unique=False)

    op.create_table(
        'rule_results',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.String(length=50), nullable=False),
        sa.Column('diagnosis_id', sa.Integer(), nullable=True),
        sa.Column('rule_name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='LOW'),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('evidence', sa.Text(), nullable=True, server_default='[]'),
        sa.Column('details', sa.Text(), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.case_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['diagnosis_id'], ['diagnoses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_rule_results_case_id', 'rule_results', ['case_id'], unique=False)
    op.create_index('ix_rule_results_diagnosis_id', 'rule_results', ['diagnosis_id'], unique=False)
    op.create_index('ix_rule_results_case_diagnosis', 'rule_results', ['case_id', 'diagnosis_id'], unique=False)

    op.create_table(
        'reviews',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.String(length=50), nullable=False),
        sa.Column('diagnosis_id', sa.Integer(), nullable=False),
        sa.Column('decision', sa.String(length=20), nullable=False),
        sa.Column('original_ai_diagnosis', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('edited_diagnosis', sa.Text(), nullable=True, server_default='{}'),
        sa.Column('final_diagnosis', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('reviewer', sa.String(length=255), nullable=False, server_default='anonymous'),
        sa.Column('review_reason', sa.Text(), nullable=True),
        sa.Column('review_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.case_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['diagnosis_id'], ['diagnoses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_reviews_case_id', 'reviews', ['case_id'], unique=False)
    op.create_index('ix_reviews_diagnosis_id', 'reviews', ['diagnosis_id'], unique=False)
    op.create_index('ix_reviews_decision', 'reviews', ['decision'], unique=False)
    op.create_index('ix_reviews_case_created', 'reviews', ['case_id', 'created_at'], unique=False)

    op.create_table(
        'verifications',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.String(length=50), nullable=False),
        sa.Column('review_id', sa.Integer(), nullable=False),
        sa.Column('verification_status', sa.String(length=20), nullable=False),
        sa.Column('verification_method', sa.String(length=100), nullable=False),
        sa.Column('verification_evidence', sa.Text(), nullable=True),
        sa.Column('before_state', sa.Text(), nullable=True, server_default='{}'),
        sa.Column('after_state', sa.Text(), nullable=True, server_default='{}'),
        sa.Column('verified_by', sa.String(length=255), nullable=False, server_default='anonymous'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.case_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['review_id'], ['reviews.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_verifications_case_id', 'verifications', ['case_id'], unique=False)
    op.create_index('ix_verifications_review_id', 'verifications', ['review_id'], unique=False)
    op.create_index('ix_verifications_verification_status', 'verifications', ['verification_status'], unique=False)
    op.create_index('ix_verifications_case_created', 'verifications', ['case_id', 'created_at'], unique=False)

    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('case_id', sa.String(length=50), nullable=True),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('actor', sa.String(length=255), nullable=False, server_default='system'),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('event_metadata', sa.Text(), nullable=True, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
        sa.ForeignKeyConstraint(['case_id'], ['cases.case_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_audit_logs_case_id', 'audit_logs', ['case_id'], unique=False)
    op.create_index('ix_audit_logs_event_type', 'audit_logs', ['event_type'], unique=False)
    op.create_index('ix_audit_logs_event_created', 'audit_logs', ['event_type', 'created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('audit_logs')
    op.drop_table('verifications')
    op.drop_table('reviews')
    op.drop_table('rule_results')
    op.drop_table('diagnoses')
    op.drop_table('cases')
