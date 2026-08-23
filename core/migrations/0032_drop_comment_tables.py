# Remove django-contrib-comments (#1130) — PHASE 2: drop the comment tables.
#
# ⛔ MERGE/DEPLOY GATE (unchanged from the previous phase-2 design):
# this migration ships as its OWN RELEASE, after the comment-free code release
# (PR #1217) has been deployed AND every Python process (apache2, celeryd,
# celerybeat) has been restarted on the target box. That restart is what ends
# comment ingress; until it happens, comment-aware code is still live and the
# tables are still reachable.
#
# ─────────────────────────────────────────────────────────────────────────────
# WHY THIS IS SMALLER THAN THE ORIGINAL PHASE 2
#
# The first phase-2 draft (PR #1218) also deleted the three comment NoticeType
# rows and the comment ContentType rows. Measured against the production
# database on 2026-08-17, that cascade was far larger than the data actually
# being retired:
#
#     django_comments rows .................    468   (130 distinct authors)
#     Notice rows destroyed by the cascade .. 22,120   of 45,291  (49%)
#                                                      spanning 2012-03-28 → 2025-03-13
#     NoticeSetting rows destroyed ..........  3,269   of 16,842  (19%)
#     django_admin_log rows destroyed .......    232
#     auth_permission rows destroyed ........     16
#
# None of that is required in order to remove django-contrib-comments:
#
#   * A `Notice` stores its ALREADY-RENDERED message text plus a FK to its
#     NoticeType. It holds no reference to a Comment (see notification.models
#     .Notice). Retaining the three NoticeTypes therefore keeps no dependency on
#     the removed app — nothing imports django_comments, and no queued batch can
#     be poisoned by their continued existence.
#   * Phase 1 already stops those notices being created (the signal receiver and
#     the comment_was_posted wiring are gone) and filters the now-unreachable
#     types out of the notification-settings UI.
#   * Stale ContentType rows are inert. If they are ever worth cleaning up, that
#     is `manage.py remove_stale_contenttypes --include-stale-apps` — the plain
#     form SKIPS apps that have been removed from INSTALLED_APPS, and Django
#     warns that dependent objects go with them. Either way it is a deliberate,
#     separately reviewable act, not a side effect of dropping two tables.
#
# So this migration destroys the 468 comments (and their 2 flag rows) and
# nothing else. Everything it does NOT do is recoverable later; what it does do
# is not. That asymmetry is the whole reason for the smaller scope.
#
# ─────────────────────────────────────────────────────────────────────────────
# WHY THERE IS NO QUEUE SCRUB HERE
#
# The previous draft re-ran the phase-1 batch scrub as a "final belt". It was
# there because deleting the NoticeType rows would break any queued batch that
# still referenced those labels. Since this migration no longer deletes them,
# that hazard does not exist.
#
# The remaining hazard — a queued batch containing a pickled
# django_comments.Comment that can no longer be unpickled — is entirely phase
# 1's responsibility and is already closed before this migration can run:
# migration 0031 clears the backlog, and the post-restart
# `manage.py scrub_comment_notice_batches` closes the migrate→restart window.
# Once every process serving this database has been restarted onto phase-1 code,
# the comment ingress path is gone and no new poisoned batch can appear in the
# days between the two releases.
#
# That last sentence has three known exceptions, all operational rather than
# structural — a fresh poisoned batch CAN appear if:
#   (a) phase-1 code is rolled back and comment-aware code serves again;
#   (b) some other host sharing this database is still running old code; or
#   (c) someone calls notification.queue() by hand with a pickled Comment.
# After any of those, repeat the phase-1 restart + scrub + queue-drain check
# before running this migration. Note the recovery is cheap either way: the
# management command still works after the tables are dropped, so a batch that
# slips through can be cleared without a rollback.
#
# Dropping these tables does not change unpickling behaviour one way or the
# other (the class became unimportable back in phase 1), so a third copy of the
# scrub logic here would add risk and no protection. Omitted deliberately.
#
# ─────────────────────────────────────────────────────────────────────────────
# SCHEMA FACTS (verified against production, 2026-08-17, via information_schema)
#
#   * The ONLY inbound FK to either table is django_comment_flags.comment_id →
#     django_comments. Nothing else in the schema references them, so dropping
#     flags first and comments second is both necessary and sufficient.
#   * Outbound FKs (to auth_user, django_site, django_content_type) are
#     unaffected by dropping the referring tables.
#   * Both tables are InnoDB.
#
# ─────────────────────────────────────────────────────────────────────────────
# IRREVERSIBILITY
#
# This migration is genuinely irreversible and now SAYS SO to Django: the
# RunSQL operation supplies no reverse_sql, so `migrate core 0031` raises
# IrreversibleError rather than silently un-recording a migration whose data is
# gone. (The previous draft used RunSQL.noop, which made Django believe the
# migration could be reversed.)
#
# Rolling phase-2 CODE back does not require unapplying this migration — there
# is no phase-2 code, only this schema change.
#
# RECOVERY: a pre-deploy RDS snapshot, taken as an explicit gate before this
# release. Record the snapshot identifier in the deploy log. Note that a
# snapshot restore is a last-resort preservation mechanism, not an ordinary
# rollback: it restores to a separate instance and requires a cutover, and any
# writes made after the snapshot are lost. If selective recovery matters,
# export django_comments/django_comment_flags to a file before deploying —
# 468 rows, trivially small.
#
# Stale 'django_comments' rows remain in django_migrations; they are inert and
# can be tidied later with `migrate --prune`.

from django.db import migrations


class Migration(migrations.Migration):

    # MySQL cannot roll back DDL, so the two DROP statements below implicitly
    # commit and cannot be undone as a unit. Declared explicitly so the
    # migration does not appear to offer atomicity it cannot deliver. If the
    # play dies between the two drops, the flags table is gone and the comments
    # table remains; re-running converges, since both use IF EXISTS.
    atomic = False

    dependencies = [
        ('core', '0031_scrub_comment_notice_batches'),
    ]

    operations = [
        # django_comment_flags carries a FK to django_comments, so it must be
        # dropped first. No reverse_sql: this is irreversible and declares it.
        migrations.RunSQL(
            sql=[
                "DROP TABLE IF EXISTS django_comment_flags;",
                "DROP TABLE IF EXISTS django_comments;",
            ],
        ),
    ]
