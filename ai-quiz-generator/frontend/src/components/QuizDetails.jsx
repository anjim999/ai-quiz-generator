export default function QuizDetails({ data }) {
  if (!data) return <p>No quiz data</p>;

  const entities = data.key_entities || {};

  return (
    <div className="space-y-4 text-sm">

      <h3 className="text-xl font-bold">{data.title}</h3>

      <a className="text-blue-600 underline" href={data.url} target="_blank">
        {data.url}
      </a>

      {/* Summary */}
      {data.summary && (
        <p className="text-gray-700">{data.summary}</p>
      )}

      {/* Entities */}
      <div>
        <h4 className="font-semibold">Key Entities</h4>
        {entities.people?.length > 0 && <p><b>People:</b> {entities.people.join(", ")}</p>}
        {entities.organizations?.length > 0 && <p><b>Organizations:</b> {entities.organizations.join(", ")}</p>}
        {entities.locations?.length > 0 && <p><b>Locations:</b> {entities.locations.join(", ")}</p>}
      </div>

      {/* Sections */}
      <div>
        <h4 className="font-semibold">Sections</h4>
        <p>{data.sections?.join(", ")}</p>
      </div>

      {/* Full Quiz */}
      <div>
        <h4 className="font-semibold mb-2">Quiz</h4>
        {data.quiz?.map((q, i) => (
          <div key={i} className="mb-4 border p-3 rounded">
            <p className="font-medium">{i + 1}. {q.question}</p>
            <ul className="list-disc pl-5 mt-1">
              {q.options.map((opt, j) => <li key={j}>{opt}</li>)}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
