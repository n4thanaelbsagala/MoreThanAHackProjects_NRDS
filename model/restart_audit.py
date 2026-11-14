"""Aggregate external restart diagnostics; never reads challenge labels."""
from collections import Counter
import statistics


def clean_restarts(reference, blocks):
    """Yield D runs immediately bordered by known H/A within the same half."""
    for _, first, last in blocks:
        i = first + 1
        while i < last:
            if reference[i] != 'D' or reference[i-1] == 'D':
                i += 1
                continue
            start = i
            while i <= last and reference[i] == 'D':
                i += 1
            if i <= last and reference[start-1] in ('H', 'A') and reference[i] in ('H', 'A'):
                end = i
                while end <= last and reference[end] == reference[i]:
                    end += 1
                yield start, i, end, reference[start-1], reference[i]


def summarize_restarts(reference, labels, blocks, fps):
    """Count delayed release and first live team at clean provider restarts."""
    if fps <= 0 or len(reference) != len(labels):
        raise ValueError('invalid inputs')
    events = list(clean_restarts(reference, blocks))
    delay = []
    outcomes = Counter()
    team_changes = Counter()
    for _, restart, live_end, previous_team, new_team in events:
        segment = labels[restart:live_end]
        first_live = next(((j, label) for j, label in enumerate(segment)
                           if label in ('H', 'A')), None)
        outcomes['reference_restarts'] += 1
        if labels[restart] == 'D':
            outcomes['predicted_D_at_restart'] += 1
        if previous_team != new_team:
            outcomes['reference_team_changed'] += 1
        else:
            outcomes['reference_team_same'] += 1
        if restart + fps < live_end:
            outcomes['eligible_after_1s'] += 1
            outcomes['still_D_after_1s'] += labels[restart + fps] == 'D'
        if restart + 3*fps < live_end:
            outcomes['eligible_after_3s'] += 1
            outcomes['still_D_after_3s'] += labels[restart + 3*fps] == 'D'
        if first_live is None:
            outcomes['no_predicted_live_before_next_reference_change'] += 1
            continue
        frames, predicted_team = first_live
        delay.append(frames)
        outcomes['first_live_correct'] += predicted_team == new_team
        outcomes['first_live_previous_team'] += predicted_team == previous_team
        outcomes['first_live_wrong'] += predicted_team != new_team
        if previous_team != new_team:
            team_changes['events'] += 1
            team_changes['predicted_previous_team'] += predicted_team == previous_team
            team_changes['predicted_new_team'] += predicted_team == new_team
    sorted_delay = sorted(delay)
    return {
        'events': dict(outcomes),
        'reference_team_changed': dict(team_changes),
        'first_live_delay_frames': {
            'count': len(delay),
            'mean': statistics.mean(delay) if delay else None,
            'median': statistics.median(delay) if delay else None,
            'p90': sorted_delay[min(len(delay)-1, int(.9*(len(delay)-1)))] if delay else None,
        },
    }
