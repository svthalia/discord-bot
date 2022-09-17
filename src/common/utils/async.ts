export const settle = async <T>(promises: Promise<T>[]) => {
  const settled = await Promise.allSettled<T>(promises);
  return (
    settled
      // eslint-disable-next-line no-undef
      .filter((res): res is PromiseFulfilledResult<Awaited<T>> => res.status === 'fulfilled')
      .map((res) => res.value)
  );
};
