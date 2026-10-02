import React from 'react';

interface Props {
  matrix: Record<string, number>;
}

export const CoverageHeatmap: React.FC<Props> = ({ matrix }) => {
  const distances = [0.25, 0.5, 1, 2, 3, 5, 8, 10, 15];
  const directions = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330];

  // Helper to snap GT values to nearest bucket
  const getClosest = (val: number, arr: number[]) => {
    return arr.reduce((prev, curr) => Math.abs(curr - val) < Math.abs(prev - val) ? curr : prev);
  };

  // Build bucketed matrix
  const bucketedMatrix: Record<string, number> = {};
  
  // Initialize
  distances.forEach(d => {
    directions.forEach(dir => {
      bucketedMatrix[`${d}_${dir}`] = 0;
    });
  });

  // Populate from actual data
  let totalCovered = 0;
  Object.entries(matrix).forEach(([key, count]) => {
    const [distStr, dirStr] = key.split('_');
    const d = getClosest(parseFloat(distStr), distances);
    const dir = getClosest(parseFloat(dirStr), directions);
    const bKey = `${d}_${dir}`;
    if (bucketedMatrix[bKey] === 0 && count > 0) totalCovered++;
    bucketedMatrix[bKey] += count;
  });

  const totalCombinations = distances.length * directions.length;
  const coveragePercent = Math.round((totalCovered / totalCombinations) * 100);

  return (
    <div className="flex flex-col items-center w-full">
      <div className="mb-6 bg-card px-6 py-3 rounded-full border border-border flex items-center gap-4">
        <span className="text-sm font-bold tracking-widest text-text-muted">TOTAL COVERAGE</span>
        <span className={`text-2xl font-bold ${coveragePercent > 75 ? 'text-green-500' : coveragePercent > 40 ? 'text-yellow-500' : 'text-red-500'}`}>
          {coveragePercent}%
        </span>
      </div>

      <div className="overflow-x-auto custom-scrollbar w-full flex justify-center pb-4">
        <table className="border-collapse">
          <thead>
            <tr>
              <th className="p-2"></th>
              {directions.map(dir => (
                <th key={dir} className="p-2 text-xs font-mono text-text-muted w-10 text-center">{dir}°</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {distances.map(dist => (
              <tr key={dist}>
                <th className="p-2 text-xs font-mono text-text-muted text-right pr-4">{dist}m</th>
                {directions.map(dir => {
                  const count = bucketedMatrix[`${dist}_${dir}`];
                  const isCovered = count > 0;
                  // Intensity based on count, max out at 10
                  const opacity = isCovered ? Math.min(1, 0.3 + (count / 10) * 0.7) : 0.1;
                  
                  return (
                    <td key={dir} className="p-1">
                      <div 
                        className={`w-8 h-8 rounded-sm ${isCovered ? 'bg-green-500' : 'bg-card-hover'}`}
                        style={{ opacity: isCovered ? opacity : 1 }}
                        title={`${dist}m, ${dir}° : ${count} samples`}
                      />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};
