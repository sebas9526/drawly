import { describe, expect, it } from 'vitest';

import { buildQueryString } from './query-string';

describe('buildQueryString', () => {
  it('returns an empty string when there are no params', () => {
    expect(buildQueryString()).toBe('');
    expect(buildQueryString({})).toBe('');
  });

  it('serializes primitives and drops null/undefined', () => {
    expect(buildQueryString({ page: 1, search: 'foo', status: undefined, sort: null })).toBe(
      '?page=1&search=foo',
    );
  });
});
