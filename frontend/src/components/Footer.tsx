import { Link } from 'react-router-dom';
import { Activity } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 mt-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-10">
          <div>
            <div className="flex items-center gap-2.5 mb-4">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Activity className="h-5 w-5 text-white" />
              </div>
              <span className="font-bold text-white text-lg">
                Medi<span className="text-blue-400">Predict</span>
              </span>
            </div>
            <p className="text-sm leading-relaxed">
              Hệ thống AI hỗ trợ dự đoán bệnh lý và gợi ý thuốc thông minh, chính xác và đáng tin cậy.
            </p>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-4">Dịch vụ</h4>
            <ul className="space-y-2">
              <li><Link to="/search" className="text-sm hover:text-white transition-colors">Tra cứu bệnh</Link></li>
              <li><Link to="/predict" className="text-sm hover:text-white transition-colors">Dự đoán AI</Link></li>
              <li><Link to="/drugs" className="text-sm hover:text-white transition-colors">Gợi ý thuốc</Link></li>
              <li><span className="text-sm hover:text-white cursor-pointer transition-colors">Tư vấn y tế</span></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-4">Thông tin</h4>
            <ul className="space-y-2">
              <li><span className="text-sm hover:text-white cursor-pointer transition-colors">Về chúng tôi</span></li>
              <li><span className="text-sm hover:text-white cursor-pointer transition-colors">Đội ngũ y tế</span></li>
              <li><span className="text-sm hover:text-white cursor-pointer transition-colors">Chính sách</span></li>
              <li><span className="text-sm hover:text-white cursor-pointer transition-colors">Điều khoản</span></li>
            </ul>
          </div>
          <div>
            <h4 className="font-semibold text-white mb-4">Liên hệ</h4>
            <ul className="space-y-2">
              <li><span className="text-sm">support@medipredict.vn</span></li>
              <li><span className="text-sm">1800-1234 (Miễn phí)</span></li>
              <li><span className="text-sm">T2-T7: 8:00-20:00</span></li>
              <li><span className="text-sm">TP. Hồ Chí Minh</span></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-slate-800 pt-6">
          <div className="bg-slate-800 rounded-xl p-4 mb-6">
            <p className="text-slate-400 text-xs text-center leading-relaxed">
              ⚠️ <strong className="text-slate-300">Lưu ý:</strong> Hệ thống chỉ hỗ trợ thông tin, không thay thế chẩn đoán y tế.
              Vui lòng tham khảo ý kiến bác sĩ trước khi sử dụng thuốc.
            </p>
          </div>
          <p className="text-slate-500 text-xs text-center">
            © 2026 MediPredict. Tất cả quyền được bảo lưu.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;