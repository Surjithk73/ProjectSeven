export default function RepairDiff({ patch }) {
  return (
    <pre className="patch-preview repair-diff" tabIndex={0} aria-label="Code changes: additions in green, removals in red">
      {patch.split("\n").map((line, index) => {
        const kind = /^(diff |index |--- |\+\+\+ )/.test(line)
          ? "file"
          : line.startsWith("@@")
            ? "hunk"
            : line.startsWith("+")
              ? "added"
              : line.startsWith("-")
                ? "removed"
                : "context";
        return (
          <span className={`repair-line repair-${kind}`} key={index}>
            {line}
          </span>
        );
      })}
    </pre>
  );
}
