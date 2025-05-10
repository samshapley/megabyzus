interface InputParamsTableProps {
  inputs: Record<string, any>;
}

export default function InputParamsTable({ inputs }: InputParamsTableProps) {
  // Convert input parameters to an array of key-value pairs
  const paramEntries = Object.entries(inputs);

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm">
        <thead>
          <tr className="border-b border-white/10">
            <th className="py-2 px-3 text-left font-medium text-secondary-text">Parameter</th>
            <th className="py-2 px-3 text-left font-medium text-secondary-text">Value</th>
          </tr>
        </thead>
        <tbody>
          {paramEntries.length > 0 ? (
            paramEntries.map(([key, value], index) => (
              <tr 
                key={key} 
                className={index < paramEntries.length - 1 ? "border-b border-white/5" : ""}
              >
                <td className="py-2 px-3 font-mono">{key}</td>
                <td className="py-2 px-3 font-mono">
                  {typeof value === 'object' 
                    ? JSON.stringify(value) 
                    : String(value)
                  }
                </td>
              </tr>
            ))
          ) : (
            <tr>
              <td colSpan={2} className="py-3 px-3 text-center text-secondary-text">
                No parameters provided
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
