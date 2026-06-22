import { Link } from 'react-router-dom';
import { ChevronRight } from 'lucide-react';

interface Disease {
  id: number | string;
  name: string;
  group_name: string;
  risk_level: string;
  icon: string;
  description: string;
  symptoms: string;
}

interface DiseaseCardProps {
  disease: Disease;
}

const getRiskBadge = (level: string) => {
  const l = level?.toLowerCase();
  if (l === 'cao' || l === 'high') return { className: 'bg-red-50 text-red-600', label: 'Nguy hiểm cao' };
  if (l === 'trung bình' || l === 'medium') return { className: 'bg-amber-50 text-amber-700', label: 'Trung bình' };
  return { className: 'bg-emerald-50 text-emerald-700', label: 'Thấp' };
};

const DiseaseCard = ({ disease }: DiseaseCardProps) => {
  const symptomsList = disease.symptoms
    ? disease.symptoms.split(',').map((s) => s.trim()).filter(Boolean).slice(0, 4)
    : [];
  const risk = getRiskBadge(disease.risk_level);

  return (
    <div className="bg-white border border-slate-200 rounded-2xl p-5 hover:shadow-lg hover:border-blue-200 transition-all duration-300 flex flex-col h-full">
      <div className="flex items-center gap-3 mb-3">
        <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center text-2xl">
          {disease.icon || '🏥'}
        </div>
        <div>
          <h4 className="font-semibold text-slate-900">{disease.name}</h4>
          <span className="inline-block px-2 py-0.5 text-xs font-medium bg-blue-50 text-blue-700 rounded-full">
            {disease.group_name}
          </span>
        </div>
      </div>

      <p className="text-sm text-slate-600 mb-3 line-clamp-2 flex-1">{disease.description}</p>

      {symptomsList.length > 0 && (
        <div className="mb-3">
          <p className="text-xs font-medium text-slate-700 mb-1.5">Triệu chứng:</p>
          <div className="flex flex-wrap gap-1.5">
            {symptomsList.map((symptom, idx) => (
              <span key={idx} className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded-full">
                {symptom}
              </span>
            ))}
          </div>
        </div>
      )}

      <div className="flex items-center justify-between mt-auto pt-3">
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${risk.className}`}>
          {risk.label}
        </span>
        <Link
          to={`/disease/${disease.id}`}
          className="text-blue-600 text-xs font-medium flex items-center gap-1 hover:gap-2 transition-all"
        >
          Xem chi tiết <ChevronRight className="h-3 w-3" />
        </Link>
      </div>
    </div>
  );
};

export default DiseaseCard;