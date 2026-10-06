export function label(value: string) {
  return value.replaceAll("_", " ").replace(/\bpct\b/g, "%");
}
