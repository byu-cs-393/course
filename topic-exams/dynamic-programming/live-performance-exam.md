# Topic Exam (Performance) — Dynamic Programming & Counting

> **New for Fall 2026.** The performance exam is the second of the three topic exams. Unlike
> the live interview, you are allowed to **practice the question ahead of time** and then
> perform it. See [Topic Exams](../README.md) for how the three exams fit together.

## The question

**[Number of Dice Rolls With Target Sum](https://leetcode.com/problems/number-of-dice-rolls-with-target-sum/)**

Count the ways to roll `n` dice with `k` faces each to reach a target sum, modulo
`10^9 + 7`. A classic counting DP — DFS with memoization over `(dice remaining, target)`, or
a bottom-up table.

## How it works

1. Practice the question above ahead of time.
2. Perform it for a TA or the instructor **in 15 minutes or less** (pass/fail).
3. Record completion in Canvas with the
   [submission template](../submission-templates.md#performance-exam).

## Learning outcomes

This exam targets the same outcomes as the [online assessment](online-assessment.md):

- Implement DP solutions using DFS with memoization (boolean, sum, min/max).
- Implement counting solutions where a formula increments a total count at each iteration (e.g., N(N-1)/2 for subsequences).
- Implement solutions that use a prefix or postfix to be more efficient.
- Implement bottom-up solutions that build from a base case iteratively.
