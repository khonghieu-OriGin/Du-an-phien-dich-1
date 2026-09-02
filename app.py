import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, abort, Response
from models import db, User, TranslatorProfile, Service, Job, Proposal, Contract, Message, DirectMessage, Deliverable, Review, LANGUAGES
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime, date
from functools import wraps

# ─── LANGUAGE LANDING PAGE CONFIGURATION ──────────────────────────────────────

LANGUAGE_PAGES = {
    "english": {
        "name": "Tiếng Anh",
        "flag": "🇬🇧",
        "slug": "english",
        "title": "Phiên Dịch Tiếng Anh",
        "subtitle": "Tìm phiên dịch viên tiếng Anh phù hợp cho công việc, hội thảo, phỏng vấn và tài liệu chuyên ngành.",
        "seo_description": "Tìm phiên dịch viên tiếng Anh chuyên nghiệp tại VietTranslate. So sánh hồ sơ, đánh giá, mức giá và chuyên môn trước khi lựa chọn.",
        "starting_price": 40000,
        "certificates": ["IELTS", "TOEIC", "VSTEP"],
        "use_cases": [
            "Phiên dịch hội nghị & sự kiện quốc tế",
            "Dịch tài liệu pháp lý & hợp đồng",
            "Phiên dịch y tế & khoa học",
            "Dịch thuật thương mại & xuất nhập khẩu",
        ],
        "seo_content": (
            "Tiếng Anh là ngôn ngữ quốc tế được sử dụng rộng rãi nhất trong giao thương, giáo dục và ngoại giao. "
            "Nhu cầu thuê phiên dịch viên tiếng Anh tại Việt Nam ngày càng tăng cao, đặc biệt trong bối cảnh hội nhập kinh tế toàn cầu. "
            "Từ các hội nghị quốc tế, đàm phán thương mại đến dịch thuật tài liệu pháp lý và y tế, phiên dịch viên tiếng Anh chuyên nghiệp đóng vai trò không thể thiếu. "
            "Khi lựa chọn phiên dịch viên tiếng Anh, bạn nên xem xét chứng chỉ (IELTS 7.0+, TOEIC 900+, hoặc VSTEP C1), kinh nghiệm trong lĩnh vực cụ thể, "
            "và khả năng phiên dịch cả hai chiều Anh-Việt, Việt-Anh một cách trơn tru. "
            "Tại VietTranslate, bạn có thể dễ dàng so sánh hồ sơ, xem đánh giá từ khách hàng thực tế và đặt dịch vụ an toàn qua hệ thống Escrow."
        ),
        "faq": [
            {
                "q": "Giá thuê phiên dịch tiếng Anh là bao nhiêu?",
                "a": "Mức giá phiên dịch tiếng Anh tham khảo từ 40.000đ trở lên, tùy vào loại hình (phiên dịch cabin, liên tục, tài liệu), thời lượng và chuyên môn yêu cầu.",
            },
            {
                "q": "Phiên dịch tiếng Anh cần chứng chỉ gì?",
                "a": "Phiên dịch viên tiếng Anh chuyên nghiệp thường có IELTS 7.0 trở lên, TOEIC 900+, hoặc VSTEP C1. Một số vị trí chuyên ngành yêu cầu bằng cấp phù hợp.",
            },
            {
                "q": "Làm thế nào để chọn phiên dịch viên tiếng Anh?",
                "a": "Hãy xem xét kinh nghiệm trong lĩnh vực cần dịch, đánh giá từ khách hàng trước, chứng chỉ ngôn ngữ và khả năng giao tiếp phản hồi nhanh.",
            },
            {
                "q": "Phiên dịch tiếng Anh có thể nhận những loại công việc nào?",
                "a": "Phiên dịch hội nghị, tòa án, y tế, thương mại, kỹ thuật, dịch tài liệu, phụ đề video, phiên dịch online qua Zoom/Teams...",
            },
        ],
    },
    "japanese": {
        "name": "Tiếng Nhật",
        "flag": "🇯🇵",
        "slug": "japanese",
        "title": "Phiên Dịch Tiếng Nhật",
        "subtitle": "Tìm phiên dịch viên tiếng Nhật phù hợp cho công việc, hội nghị, giao tiếp kinh doanh và các nhu cầu chuyên môn.",
        "seo_description": "Tìm phiên dịch viên tiếng Nhật chuyên nghiệp tại VietTranslate. Xem hồ sơ, đánh giá, mức giá và kinh nghiệm để lựa chọn phiên dịch viên phù hợp.",
        "starting_price": 30000,
        "certificates": ["JLPT N2 trở lên"],
        "use_cases": [
            "Phiên dịch làm việc với doanh nghiệp Nhật Bản",
            "Dịch tài liệu kỹ thuật & bản vẽ",
            "Phiên dịch xuất khẩu lao động Nhật Bản",
            "Dịch hợp đồng & tài liệu pháp lý Nhật-Việt",
        ],
        "seo_content": (
            "Tiếng Nhật là ngôn ngữ đặc thù với ba bộ chữ Hiragana, Katakana và Kanji, đòi hỏi phiên dịch viên phải đạt trình độ học thuật cao. "
            "Quan hệ thương mại Việt–Nhật ngày càng phát triển, kéo theo nhu cầu lớn về phiên dịch trong lĩnh vực sản xuất, FDI, xuất khẩu lao động và hợp tác kỹ thuật. "
            "Phiên dịch viên tiếng Nhật giỏi không chỉ thông thạo ngôn ngữ mà còn phải hiểu văn hóa doanh nghiệp Nhật Bản — tính cẩn thận, tôn trọng thứ bậc và giao tiếp gián tiếp. "
            "Khi chọn phiên dịch viên tiếng Nhật, hãy ưu tiên người có JLPT N2 trở lên và kinh nghiệm thực tế trong ngành bạn cần. "
            "VietTranslate kết nối bạn với đội ngũ phiên dịch viên tiếng Nhật uy tín, được đánh giá bởi khách hàng thực tế."
        ),
        "faq": [
            {
                "q": "Giá thuê phiên dịch tiếng Nhật là bao nhiêu?",
                "a": "Mức giá tham khảo từ 30.000đ, tùy vào loại hình phiên dịch, thời lượng và chuyên môn. Phiên dịch kỹ thuật hoặc tài liệu pháp lý thường có mức giá cao hơn.",
            },
            {
                "q": "Phiên dịch tiếng Nhật cần chứng chỉ gì?",
                "a": "Phiên dịch viên tiếng Nhật chuyên nghiệp thường có chứng chỉ JLPT N2 trở lên. Với công việc kỹ thuật cao, JLPT N1 được ưu tiên.",
            },
            {
                "q": "Làm thế nào để chọn phiên dịch viên tiếng Nhật?",
                "a": "Xem xét trình độ JLPT, kinh nghiệm trong lĩnh vực cụ thể (kỹ thuật, pháp lý, y tế), đánh giá từ khách hàng và khả năng hiểu văn hóa Nhật.",
            },
            {
                "q": "Phiên dịch tiếng Nhật có thể nhận những loại công việc nào?",
                "a": "Phiên dịch hội nghị với đối tác Nhật, dịch tài liệu kỹ thuật, hồ sơ xuất khẩu lao động, hợp đồng thương mại, phiên dịch nhà máy, dịch manga/anime chuyên nghiệp.",
            },
        ],
    },
    "korean": {
        "name": "Tiếng Hàn",
        "flag": "🇰🇷",
        "slug": "korean",
        "title": "Phiên Dịch Tiếng Hàn",
        "subtitle": "Kết nối với phiên dịch viên tiếng Hàn có kinh nghiệm cho mọi nhu cầu kinh doanh, giáo dục và văn hóa.",
        "seo_description": "Tìm phiên dịch viên tiếng Hàn chuyên nghiệp tại VietTranslate. So sánh hồ sơ, mức giá và đánh giá để chọn người phù hợp nhất.",
        "starting_price": 35000,
        "certificates": ["TOPIK 4 trở lên"],
        "use_cases": [
            "Phiên dịch làm việc với doanh nghiệp Hàn Quốc",
            "Dịch hồ sơ xuất khẩu lao động Hàn Quốc (EPS-TOPIK)",
            "Phiên dịch hội nghị & đàm phán thương mại",
            "Dịch nội dung K-pop, phim, truyện tranh",
        ],
        "seo_content": (
            "Quan hệ Việt–Hàn đang ở giai đoạn phát triển mạnh với hàng nghìn doanh nghiệp Hàn Quốc đầu tư vào Việt Nam. "
            "Nhu cầu phiên dịch tiếng Hàn rất đa dạng: từ môi trường nhà máy, văn phòng doanh nghiệp đến các lĩnh vực văn hóa, giải trí và du học. "
            "Phiên dịch viên tiếng Hàn cần thành thạo cả Hangul lẫn văn hóa giao tiếp Hàn Quốc. Chứng chỉ TOPIK cấp 4 trở lên là tiêu chuẩn tối thiểu cho phiên dịch chuyên nghiệp. "
            "Tại VietTranslate, bạn có thể tìm phiên dịch viên tiếng Hàn theo chuyên ngành, xem đánh giá thực tế và đặt dịch vụ với chi phí minh bạch."
        ),
        "faq": [
            {
                "q": "Giá thuê phiên dịch tiếng Hàn là bao nhiêu?",
                "a": "Mức giá tham khảo từ 35.000đ, tùy theo loại hình và thời lượng phiên dịch.",
            },
            {
                "q": "Phiên dịch tiếng Hàn cần chứng chỉ gì?",
                "a": "Phiên dịch viên tiếng Hàn thường có TOPIK cấp 4 (điểm 200+) trở lên. Các vị trí cao cấp yêu cầu TOPIK cấp 5 hoặc 6.",
            },
            {
                "q": "Làm thế nào để chọn phiên dịch viên tiếng Hàn phù hợp?",
                "a": "Xem xét cấp TOPIK, kinh nghiệm trong ngành (sản xuất, pháp lý, giải trí), đánh giá từ khách hàng và tốc độ phản hồi.",
            },
            {
                "q": "Phiên dịch tiếng Hàn phù hợp với những lĩnh vực nào?",
                "a": "Nhà máy, doanh nghiệp FDI Hàn Quốc, EPS-TOPIK, K-beauty, K-pop, phim truyền hình, du học Hàn Quốc, hợp đồng thương mại.",
            },
        ],
    },
    "chinese": {
        "name": "Tiếng Trung",
        "flag": "🇨🇳",
        "slug": "chinese",
        "title": "Phiên Dịch Tiếng Trung",
        "subtitle": "Tìm phiên dịch viên tiếng Trung (Quan Thoại/Quảng Đông) cho thương mại, kỹ thuật và giao tiếp doanh nghiệp.",
        "seo_description": "Tìm phiên dịch viên tiếng Trung chuyên nghiệp tại VietTranslate. Xem hồ sơ, đánh giá và mức giá để lựa chọn người phù hợp.",
        "starting_price": 30000,
        "certificates": ["HSK 5 trở lên"],
        "use_cases": [
            "Phiên dịch thương mại Việt–Trung",
            "Dịch tài liệu kỹ thuật & bản vẽ từ Trung Quốc",
            "Phiên dịch đàm phán nhập khẩu hàng hóa",
            "Dịch hợp đồng & chứng từ xuất nhập khẩu",
        ],
        "seo_content": (
            "Trung Quốc là đối tác thương mại lớn nhất của Việt Nam, tạo ra nhu cầu khổng lồ về phiên dịch tiếng Trung trong kinh doanh, thương mại và sản xuất. "
            "Phiên dịch viên tiếng Trung cần phân biệt rõ tiếng Phổ Thông (Quan Thoại) và tiếng Quảng Đông, cũng như chữ Giản Thể và Phồn Thể. "
            "Chứng chỉ HSK (Hanyu Shuiping Kaoshi) cấp 5 trở lên là tiêu chuẩn cho phiên dịch chuyên nghiệp. "
            "Tại VietTranslate, bạn có thể tìm phiên dịch viên tiếng Trung theo từng chuyên ngành, đảm bảo chính xác và hiệu quả trong giao tiếp thương mại."
        ),
        "faq": [
            {
                "q": "Giá thuê phiên dịch tiếng Trung là bao nhiêu?",
                "a": "Mức giá tham khảo từ 30.000đ, tùy theo phương ngữ (Quan Thoại/Quảng Đông), loại hình và thời lượng.",
            },
            {
                "q": "Phiên dịch tiếng Trung cần chứng chỉ gì?",
                "a": "Phiên dịch viên tiếng Trung thường có HSK 5 trở lên. Một số vị trí yêu cầu HSK 6 hoặc bằng cử nhân tiếng Trung.",
            },
            {
                "q": "Làm thế nào để chọn phiên dịch viên tiếng Trung?",
                "a": "Xác định phương ngữ cần (Quan Thoại hay Quảng Đông), xem chứng chỉ HSK, kinh nghiệm thương mại và đánh giá từ khách hàng.",
            },
            {
                "q": "Phiên dịch tiếng Trung phù hợp với những lĩnh vực nào?",
                "a": "Thương mại xuất nhập khẩu, đàm phán với đối tác Trung Quốc, dịch tài liệu kỹ thuật, hội nghị doanh nghiệp, dịch nội dung số.",
            },
        ],
    },
    "russian": {
        "name": "Tiếng Nga",
        "flag": "🇷🇺",
        "slug": "russian",
        "title": "Phiên Dịch Tiếng Nga",
        "subtitle": "Tìm phiên dịch viên tiếng Nga chuyên nghiệp cho ngoại giao, kỹ thuật, khoa học và hợp tác quốc tế.",
        "seo_description": "Tìm phiên dịch viên tiếng Nga chuyên nghiệp tại VietTranslate. So sánh hồ sơ, mức giá và kinh nghiệm để lựa chọn phù hợp.",
        "starting_price": 45000,
        "certificates": ["ТРКИ B2 trở lên"],
        "use_cases": [
            "Phiên dịch hợp tác kỹ thuật & khoa học",
            "Dịch tài liệu ngoại giao & quốc phòng",
            "Phiên dịch năng lượng & dầu khí",
            "Dịch văn học & nghiên cứu học thuật",
        ],
        "seo_content": (
            "Tiếng Nga là ngôn ngữ chính thức của Liên bang Nga và được sử dụng rộng rãi ở nhiều quốc gia thuộc Liên Xô cũ. "
            "Quan hệ Việt–Nga có lịch sử lâu dài trong lĩnh vực giáo dục, khoa học, quốc phòng và năng lượng. "
            "Phiên dịch viên tiếng Nga chuyên nghiệp thường có kiến thức sâu về khoa học kỹ thuật hoặc ngoại giao. "
            "Tại VietTranslate, bạn có thể tìm phiên dịch viên tiếng Nga phù hợp với yêu cầu chuyên môn của mình."
        ),
        "faq": [
            {
                "q": "Giá thuê phiên dịch tiếng Nga là bao nhiêu?",
                "a": "Mức giá tham khảo từ 45.000đ, phụ thuộc vào chuyên ngành và thời lượng yêu cầu.",
            },
            {
                "q": "Phiên dịch tiếng Nga cần yêu cầu chuyên môn gì?",
                "a": "Yêu cầu chuyên môn tùy theo từng công việc. Phiên dịch kỹ thuật thường yêu cầu nền tảng khoa học; phiên dịch ngoại giao yêu cầu kinh nghiệm thực tế.",
            },
            {
                "q": "Làm thế nào để chọn phiên dịch viên tiếng Nga?",
                "a": "Xem xét kinh nghiệm trong lĩnh vực cụ thể, khả năng phiên dịch 2 chiều, đánh giá từ khách hàng và bằng cấp học thuật liên quan.",
            },
            {
                "q": "Phiên dịch tiếng Nga phù hợp với những lĩnh vực nào?",
                "a": "Hợp tác kỹ thuật, dầu khí, nghiên cứu khoa học, ngoại giao, giáo dục, du lịch và văn học.",
            },
        ],
    },
    "thai": {
        "name": "Tiếng Thái",
        "flag": "🇹🇭",
        "slug": "thai",
        "title": "Phiên Dịch Tiếng Thái",
        "subtitle": "Tìm phiên dịch viên tiếng Thái cho thương mại, du lịch và hợp tác khu vực ASEAN.",
        "seo_description": "Tìm phiên dịch viên tiếng Thái chuyên nghiệp tại VietTranslate. Xem hồ sơ và đánh giá để chọn người phù hợp.",
        "starting_price": 40000,
        "certificates": None,
        "use_cases": [
            "Phiên dịch thương mại ASEAN",
            "Dịch hợp đồng & tài liệu pháp lý Thái–Việt",
            "Phiên dịch du lịch & khách sạn",
            "Dịch nội dung truyền thông & giải trí",
        ],
        "seo_content": (
            "Thái Lan và Việt Nam là hai nền kinh tế lớn trong khối ASEAN với quan hệ thương mại ngày càng mở rộng. "
            "Nhu cầu phiên dịch tiếng Thái tập trung chủ yếu vào thương mại, nông nghiệp, du lịch và đầu tư FDI. "
            "Tiếng Thái có hệ thống chữ viết và thanh điệu đặc trưng, đòi hỏi phiên dịch viên được đào tạo chuyên biệt. "
            "VietTranslate kết nối bạn với phiên dịch viên tiếng Thái uy tín, phù hợp với nhu cầu thực tế của bạn."
        ),
        "faq": [
            {
                "q": "Giá thuê phiên dịch tiếng Thái là bao nhiêu?",
                "a": "Mức giá tham khảo từ 40.000đ, tùy theo loại hình và thời lượng phiên dịch.",
            },
            {
                "q": "Phiên dịch tiếng Thái cần yêu cầu chuyên môn gì?",
                "a": "Yêu cầu chuyên môn tùy theo từng công việc. Liên hệ trực tiếp với phiên dịch viên để thảo luận về yêu cầu cụ thể.",
            },
            {
                "q": "Phiên dịch tiếng Thái phù hợp với những lĩnh vực nào?",
                "a": "Thương mại ASEAN, du lịch, nông nghiệp, hợp đồng đầu tư, nội dung truyền thông và giải trí.",
            },
            {
                "q": "Làm thế nào để chọn phiên dịch viên tiếng Thái?",
                "a": "Xem xét kinh nghiệm trong lĩnh vực cần dịch, đánh giá từ khách hàng trước và khả năng phản hồi nhanh.",
            },
        ],
    },
    "french": {
        "name": "Tiếng Pháp",
        "flag": "🇫🇷",
        "slug": "french",
        "title": "Phiên Dịch Tiếng Pháp",
        "subtitle": "Tìm phiên dịch viên tiếng Pháp cho ngoại giao, pháp lý, văn hóa và hợp tác quốc tế Pháp ngữ.",
        "seo_description": "Tìm phiên dịch viên tiếng Pháp chuyên nghiệp tại VietTranslate. So sánh hồ sơ, mức giá và chuyên môn để lựa chọn phù hợp.",
        "starting_price": 45000,
        "certificates": ["DELF B2 trở lên"],
        "use_cases": [
            "Phiên dịch ngoại giao & tổ chức quốc tế",
            "Dịch tài liệu pháp lý & hành chính Pháp ngữ",
            "Phiên dịch văn hóa & nghệ thuật",
            "Dịch học thuật & nghiên cứu khoa học",
        ],
        "seo_content": (
            "Tiếng Pháp là ngôn ngữ chính thức của 29 quốc gia và là ngôn ngữ làm việc của nhiều tổ chức quốc tế lớn như Liên Hợp Quốc, EU. "
            "Việt Nam có lịch sử gắn bó với tiếng Pháp và hiện có cộng đồng Pháp ngữ đáng kể. "
            "Phiên dịch viên tiếng Pháp thường hoạt động trong lĩnh vực ngoại giao, pháp lý, giáo dục và văn hóa. "
            "Chứng chỉ DELF B2 trở lên là tiêu chuẩn tối thiểu, với các vị trí cao cấp yêu cầu DALF C1/C2. "
            "Tại VietTranslate, bạn có thể tìm phiên dịch viên tiếng Pháp uy tín với đánh giá minh bạch từ khách hàng thực tế."
        ),
        "faq": [
            {
                "q": "Giá thuê phiên dịch tiếng Pháp là bao nhiêu?",
                "a": "Mức giá tham khảo từ 45.000đ, tùy theo chuyên ngành và thời lượng yêu cầu.",
            },
            {
                "q": "Phiên dịch tiếng Pháp cần chứng chỉ gì?",
                "a": "Phiên dịch viên tiếng Pháp chuyên nghiệp thường có DELF B2 trở lên hoặc DALF C1/C2. Một số có bằng cử nhân tiếng Pháp hoặc ngành liên quan.",
            },
            {
                "q": "Phiên dịch tiếng Pháp phù hợp với những lĩnh vực nào?",
                "a": "Ngoại giao, tổ chức quốc tế, pháp lý, giáo dục đại học, nghiên cứu khoa học, văn hóa nghệ thuật và du lịch.",
            },
            {
                "q": "Làm thế nào để chọn phiên dịch viên tiếng Pháp?",
                "a": "Xem xét chứng chỉ DELF/DALF, kinh nghiệm trong lĩnh vực cụ thể, khả năng phiên dịch hai chiều và đánh giá từ khách hàng.",
            },
        ],
    },
    "german": {
        "name": "Tiếng Đức",
        "flag": "🇩🇪",
        "slug": "german",
        "title": "Phiên Dịch Tiếng Đức",
        "subtitle": "Tìm phiên dịch viên tiếng Đức cho kỹ thuật, sản xuất, xuất nhập khẩu và hợp tác với doanh nghiệp Đức.",
        "seo_description": "Tìm phiên dịch viên tiếng Đức chuyên nghiệp tại VietTranslate. So sánh hồ sơ, đánh giá và mức giá để chọn người phù hợp.",
        "starting_price": 50000,
        "certificates": ["TestDaF / Goethe B2"],
        "use_cases": [
            "Phiên dịch làm việc với doanh nghiệp Đức & châu Âu",
            "Dịch tài liệu kỹ thuật & máy móc nhập khẩu",
            "Phiên dịch hội nghị thương mại",
            "Hỗ trợ du học & định cư tại Đức",
        ],
        "seo_content": (
            "Đức là nền kinh tế lớn nhất châu Âu và là đối tác thương mại quan trọng của Việt Nam trong lĩnh vực máy móc, thiết bị và công nghệ cao. "
            "Phiên dịch tiếng Đức đòi hỏi độ chính xác cao do tiếng Đức có cấu trúc ngữ pháp phức tạp và nhiều thuật ngữ kỹ thuật chuyên biệt. "
            "Chứng chỉ Goethe B2 hoặc TestDaF là tiêu chuẩn phổ biến, với các vị trí cao cấp yêu cầu C1/C2. "
            "Tại VietTranslate, bạn có thể tìm phiên dịch viên tiếng Đức giàu kinh nghiệm, đặc biệt trong lĩnh vực kỹ thuật và thương mại quốc tế."
        ),
        "faq": [
            {
                "q": "Giá thuê phiên dịch tiếng Đức là bao nhiêu?",
                "a": "Mức giá tham khảo từ 50.000đ, tùy theo chuyên ngành và mức độ phức tạp của nội dung.",
            },
            {
                "q": "Phiên dịch tiếng Đức cần chứng chỉ gì?",
                "a": "Phiên dịch tiếng Đức chuyên nghiệp thường có Goethe B2 trở lên hoặc TestDaF. Vị trí kỹ thuật có thể yêu cầu bằng cấp chuyên ngành.",
            },
            {
                "q": "Phiên dịch tiếng Đức phù hợp với những lĩnh vực nào?",
                "a": "Kỹ thuật, máy móc thiết bị, ô tô, dược phẩm, hóa chất, thương mại quốc tế, hỗ trợ du học Đức.",
            },
            {
                "q": "Làm thế nào để chọn phiên dịch viên tiếng Đức?",
                "a": "Xem xét chứng chỉ ngôn ngữ, kiến thức chuyên ngành kỹ thuật, đánh giá từ khách hàng và khả năng phản hồi nhanh.",
            },
        ],
    },
    "portuguese": {
        "name": "Tiếng Bồ Đào Nha",
        "flag": "🇵🇹",
        "slug": "portuguese",
        "title": "Phiên Dịch Tiếng Bồ Đào Nha",
        "subtitle": "Tìm phiên dịch viên tiếng Bồ Đào Nha (Brazil/Portugal) cho thương mại, đầu tư và hợp tác quốc tế.",
        "seo_description": "Tìm phiên dịch viên tiếng Bồ Đào Nha chuyên nghiệp tại VietTranslate. Xem hồ sơ và đánh giá để lựa chọn phù hợp.",
        "starting_price": 50000,
        "certificates": ["CELPE-Bras"],
        "use_cases": [
            "Phiên dịch thương mại với đối tác Brazil & Bồ Đào Nha",
            "Dịch tài liệu nông nghiệp & thực phẩm",
            "Phiên dịch hội nghị quốc tế",
            "Dịch nội dung truyền thông Lusophone",
        ],
        "seo_content": (
            "Tiếng Bồ Đào Nha là ngôn ngữ của hơn 250 triệu người trên thế giới, đặc biệt tại Brazil — nền kinh tế lớn nhất Nam Mỹ. "
            "Việt Nam có quan hệ thương mại ngày càng phát triển với Brazil trong lĩnh vực nông nghiệp, thực phẩm và hàng hóa tiêu dùng. "
            "Phiên dịch viên tiếng Bồ Đào Nha cần phân biệt rõ tiếng Bồ Đào Nha của Brazil và Bồ Đào Nha (châu Âu). "
            "Tại VietTranslate, bạn có thể tìm phiên dịch viên tiếng Bồ Đào Nha phù hợp với nhu cầu cụ thể của mình."
        ),
        "faq": [
            {
                "q": "Giá thuê phiên dịch tiếng Bồ Đào Nha là bao nhiêu?",
                "a": "Mức giá tham khảo từ 50.000đ, tùy theo phương ngữ (Brazil hay Bồ Đào Nha), loại hình và thời lượng.",
            },
            {
                "q": "Phiên dịch tiếng Bồ Đào Nha cần chứng chỉ gì?",
                "a": "Chứng chỉ CELPE-Bras (Brazil) là phổ biến. Yêu cầu chuyên môn cụ thể tùy theo từng công việc.",
            },
            {
                "q": "Phiên dịch tiếng Bồ Đào Nha phù hợp với những lĩnh vực nào?",
                "a": "Thương mại nông sản, xuất nhập khẩu, đầu tư quốc tế, nội dung truyền thông, nghiên cứu học thuật.",
            },
            {
                "q": "Làm thế nào để chọn phiên dịch viên tiếng Bồ Đào Nha?",
                "a": "Xác định phương ngữ cần (Brazil hay châu Âu), xem kinh nghiệm thực tế, đánh giá từ khách hàng và chuyên môn lĩnh vực.",
            },
        ],
    },
    "spanish": {
        "name": "Tiếng Tây Ban Nha",
        "flag": "🇪🇸",
        "slug": "spanish",
        "title": "Phiên Dịch Tiếng Tây Ban Nha",
        "subtitle": "Tìm phiên dịch viên tiếng Tây Ban Nha cho thương mại quốc tế, pháp lý và hợp tác với thị trường Mỹ Latinh.",
        "seo_description": "Tìm phiên dịch viên tiếng Tây Ban Nha chuyên nghiệp tại VietTranslate. So sánh hồ sơ, mức giá và kinh nghiệm để lựa chọn phù hợp.",
        "starting_price": 50000,
        "certificates": ["DELE B2 trở lên"],
        "use_cases": [
            "Phiên dịch thương mại với thị trường Mỹ Latinh",
            "Dịch tài liệu pháp lý & hợp đồng",
            "Phiên dịch hội nghị quốc tế",
            "Dịch nội dung marketing & truyền thông",
        ],
        "seo_content": (
            "Tiếng Tây Ban Nha là ngôn ngữ được nói nhiều thứ hai trên thế giới, với hơn 500 triệu người sử dụng tại Tây Ban Nha và 20 quốc gia Mỹ Latinh. "
            "Nhu cầu phiên dịch tiếng Tây Ban Nha tại Việt Nam đang tăng trong bối cảnh mở rộng quan hệ thương mại với các nước Mỹ Latinh. "
            "Phiên dịch viên tiếng Tây Ban Nha cần nắm rõ sự khác biệt giữa tiếng Tây Ban Nha Châu Âu và các phương ngữ Mỹ Latinh. "
            "Tại VietTranslate, bạn có thể tìm phiên dịch viên tiếng Tây Ban Nha phù hợp với thị trường mục tiêu của mình."
        ),
        "faq": [
            {
                "q": "Giá thuê phiên dịch tiếng Tây Ban Nha là bao nhiêu?",
                "a": "Mức giá tham khảo từ 50.000đ, tùy theo phương ngữ, loại hình và thời lượng phiên dịch.",
            },
            {
                "q": "Phiên dịch tiếng Tây Ban Nha cần chứng chỉ gì?",
                "a": "Phiên dịch viên tiếng Tây Ban Nha thường có DELE B2 trở lên. Một số có bằng cử nhân tiếng Tây Ban Nha hoặc SIELE.",
            },
            {
                "q": "Phiên dịch tiếng Tây Ban Nha phù hợp với những lĩnh vực nào?",
                "a": "Thương mại quốc tế, nông sản, năng lượng tái tạo, pháp lý, marketing, du lịch và nghiên cứu học thuật.",
            },
            {
                "q": "Làm thế nào để chọn phiên dịch viên tiếng Tây Ban Nha?",
                "a": "Xác định phương ngữ (Châu Âu hay Mỹ Latinh), xem chứng chỉ DELE, kinh nghiệm trong ngành và đánh giá khách hàng.",
            },
        ],
    },
}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = os.path.join('static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

# ─── DECORATORS ────────────────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để tiếp tục.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash('Bạn không có quyền truy cập trang này.', 'error')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated

@app.context_processor
def inject_globals():
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return dict(current_user=user, LANGUAGES=LANGUAGES)

# ─── PUBLIC ROUTES ─────────────────────────────────────────────────────────────

@app.route('/')
def index():
    top_translators = TranslatorProfile.query.filter_by(is_verified=True).order_by(
        TranslatorProfile.rating.desc()).limit(4).all()
    if not top_translators:
        top_translators = TranslatorProfile.query.order_by(TranslatorProfile.rating.desc()).limit(4).all()
    latest_jobs = Job.query.filter_by(status='open', is_flagged=False).order_by(Job.created_at.desc()).limit(4).all()
    return render_template('index.html', top_translators=top_translators, latest_jobs=latest_jobs)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/payment-info')
def payment_info():
    return render_template('payment_info.html')

# ─── AUTH ──────────────────────────────────────────────────────────────────────

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and user.is_active and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            flash('Đăng nhập thành công!', 'success')
            if user.is_admin:
                return redirect(url_for('admin_dashboard'))
            return redirect(url_for('index'))
        else:
            flash('Email hoặc mật khẩu không đúng, hoặc tài khoản đã bị khoá.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        phone = request.form.get('phone')
        role = request.form.get('role')

        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng.', 'error')
            return redirect(url_for('register'))

        new_user = User(name=name, email=email,
                        password_hash=generate_password_hash(password),
                        phone=phone, role=role)
        db.session.add(new_user)
        db.session.commit()

        if role == 'translator':
            profile = TranslatorProfile(user_id=new_user.id)
            db.session.add(profile)
            db.session.commit()

        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Đã đăng xuất.', 'success')
    return redirect(url_for('index'))

# ─── ACCOUNT ───────────────────────────────────────────────────────────────────

@app.route('/account', methods=['GET', 'POST'])
@login_required
def account_profile():
    user = User.query.get(session['user_id'])
    if request.method == 'POST':
        action = request.form.get('action', 'basic')

        if action == 'basic':
            user.name = request.form.get('name', user.name).strip()
            user.phone = request.form.get('phone', user.phone or '').strip()
            db.session.commit()
            flash('Đã cập nhật thông tin cơ bản!', 'success')

        elif action == 'translator_profile' and user.role == 'translator':
            profile = user.profile
            if not profile:
                profile = TranslatorProfile(user_id=user.id)
                db.session.add(profile)
            profile.title = request.form.get('title', '').strip()
            profile.bio = request.form.get('bio', '').strip()
            profile.languages = request.form.get('languages', '').strip()
            profile.badges = request.form.get('badges', '').strip()
            profile.response_time = request.form.get('response_time', '< 1 giờ').strip()
            db.session.commit()
            flash('Đã cập nhật hồ sơ phiên dịch viên!', 'success')

        elif action == 'change_password':
            old_pw = request.form.get('old_password', '')
            new_pw = request.form.get('new_password', '')
            confirm_pw = request.form.get('confirm_password', '')
            if not check_password_hash(user.password_hash, old_pw):
                flash('Mật khẩu hiện tại không đúng.', 'error')
            elif new_pw != confirm_pw:
                flash('Mật khẩu mới không khớp.', 'error')
            elif len(new_pw) < 6:
                flash('Mật khẩu mới phải ít nhất 6 ký tự.', 'error')
            else:
                user.password_hash = generate_password_hash(new_pw)
                db.session.commit()
                flash('Đã đổi mật khẩu thành công!', 'success')

        return redirect(url_for('account_profile'))
    return render_template('account_profile.html', user=user)

@app.route('/account/history')
@login_required
def account_history():
    user = User.query.get(session['user_id'])
    if user.role == 'hirer':
        contracts = Contract.query.filter_by(hirer_id=user.id).order_by(Contract.created_at.desc()).all()
    else:
        contracts = Contract.query.filter_by(translator_id=user.id).order_by(Contract.created_at.desc()).all()
    return render_template('account_history.html', user=user, contracts=contracts)

# ─── FLOW 1: TÌM PHIÊN DỊCH VIÊN ──────────────────────────────────────────────

@app.route('/translator')
def translator_list():
    lang = request.args.get('lang', '')
    rating_filter = request.args.get('rating', '')
    page = request.args.get('page', 1, type=int)
    per_page = 9

    query = TranslatorProfile.query
    if lang:
        query = query.filter(TranslatorProfile.languages.ilike(f'%{lang}%'))
    if rating_filter:
        query = query.filter(TranslatorProfile.rating >= float(rating_filter))

    pagination = query.order_by(TranslatorProfile.rating.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('translator_list.html', profiles=pagination.items,
                           pagination=pagination, lang_filter=lang, LANGUAGES=LANGUAGES)

@app.route('/api/translators')
def api_translators():
    """JSON API cho client-side filtering realtime."""
    profiles = TranslatorProfile.query.order_by(TranslatorProfile.rating.desc()).all()
    data = []
    for p in profiles:
        # Lấy giá thấp nhất từ services
        min_price = None
        if p.services:
            prices = [s.basic_price for s in p.services if s.basic_price]
            min_price = min(prices) if prices else None

        # Lấy thời gian hoàn thành thấp nhất từ services (parse số ngày)
        min_days = None
        if p.services:
            for s in p.services:
                for field in [s.basic_delivery, s.standard_delivery, s.premium_delivery]:
                    if field:
                        import re
                        nums = re.findall(r'\d+', field)
                        if nums:
                            d = int(nums[0])
                            if min_days is None or d < min_days:
                                min_days = d

        # Tách languages và badges thành list
        langs = [l.strip() for l in (p.languages or '').split(',') if l.strip()]
        badges = [b.strip() for b in (p.badges or '').split(',') if b.strip()]

        data.append({
            'id': p.id,
            'user_id': p.user_id,
            'name': p.user.name,
            'initial': p.user.name[0].upper() if p.user.name else '?',
            'title': p.title or '',
            'languages': langs,
            'badges': badges,
            'rating': float(p.rating or 0),
            'total_reviews': p.total_reviews or 0,
            'min_price': min_price,
            'completion_days': min_days,
            'is_verified': p.is_verified,
            'profile_url': url_for('translator_profile', profile_id=p.id),
            'chat_url': url_for('direct_chat', translator_user_id=p.user_id),
        })
    return jsonify(data)

@app.route('/translator/<int:profile_id>')
def translator_profile(profile_id):
    profile = TranslatorProfile.query.get_or_404(profile_id)
    # Reviews received by this translator
    reviews = Review.query.filter_by(reviewee_id=profile.user_id).order_by(Review.created_at.desc()).limit(10).all()
    return render_template('translator_profile.html', profile=profile, reviews=reviews)

@app.route('/translator/<string:lang_slug>')
def translator_language(lang_slug):
    """SEO landing page theo từng ngôn ngữ."""
    lang_config = LANGUAGE_PAGES.get(lang_slug)
    if not lang_config:
        abort(404)
    # Các ngôn ngữ khác để internal linking
    other_languages = {k: v for k, v in LANGUAGE_PAGES.items() if k != lang_slug}
    return render_template(
        'translator_language.html',
        lang=lang_config,
        other_languages=other_languages,
    )

@app.route('/sitemap.xml')
def sitemap():
    """Sitemap XML chứa tất cả language landing pages."""
    base_url = request.url_root.rstrip('/')
    urls = [
        {'loc': f"{base_url}/translator", 'priority': '0.9'},
    ]
    for slug in LANGUAGE_PAGES:
        urls.append({'loc': f"{base_url}/translator/{slug}", 'priority': '0.8'})
    urls += [
        {'loc': f"{base_url}/", 'priority': '1.0'},
        {'loc': f"{base_url}/jobs", 'priority': '0.7'},
        {'loc': f"{base_url}/about", 'priority': '0.5'},
    ]
    xml = render_template('sitemap.xml', urls=urls)
    return Response(xml, mimetype='application/xml')



# ─── DIRECT CHAT ───────────────────────────────────────────────────────────────

@app.route('/chat/<int:translator_user_id>')
@login_required
def direct_chat(translator_user_id):
    if session['user_id'] == translator_user_id:
        return redirect(url_for('index'))
    translator = User.query.get_or_404(translator_user_id)
    return render_template('chat.html', other_user=translator)

@app.route('/api/direct-messages/<int:other_user_id>')
@login_required
def get_direct_messages(other_user_id):
    me = session['user_id']
    msgs = DirectMessage.query.filter(
        db.or_(
            db.and_(DirectMessage.sender_id == me, DirectMessage.receiver_id == other_user_id),
            db.and_(DirectMessage.sender_id == other_user_id, DirectMessage.receiver_id == me)
        )
    ).order_by(DirectMessage.created_at.asc()).all()
    return jsonify([{
        'id': m.id, 'sender_id': m.sender_id, 'sender_name': m.sender.name,
        'content': m.content, 'time': m.created_at.strftime('%H:%M %d/%m')
    } for m in msgs])

@app.route('/api/direct-messages/<int:other_user_id>', methods=['POST'])
@login_required
def send_direct_message(other_user_id):
    content = request.json.get('content', '').strip()
    if content:
        msg = DirectMessage(sender_id=session['user_id'], receiver_id=other_user_id, content=content)
        db.session.add(msg)
        db.session.commit()
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'}), 400

# ─── DIRECT BOOKING ────────────────────────────────────────────────────────────

@app.route('/book/<int:service_id>', methods=['GET', 'POST'])
@login_required
def book_service(service_id):
    service = Service.query.get_or_404(service_id)
    tier = request.args.get('tier', 'basic')
    prices = {'basic': service.basic_price, 'standard': service.standard_price,
              'premium': service.premium_price}
    price = prices.get(tier, service.basic_price)

    if request.method == 'POST':
        contract = Contract(
            service_id=service.id,
            hirer_id=session['user_id'],
            translator_id=service.profile.user_id,
            agreed_price=int(request.form.get('price', price)),
            scheduled_date=request.form.get('scheduled_date', ''),
            scheduled_time_start=request.form.get('time_start', ''),
            scheduled_time_end=request.form.get('time_end', ''),
            location=request.form.get('location', ''),
            status='escrow_pending'
        )
        db.session.add(contract)
        db.session.commit()
        flash('Đặt dịch vụ thành công! Vui lòng thanh toán Escrow để bắt đầu.', 'success')
        return redirect(url_for('payment_mockup', contract_id=contract.id))

    # Extract fixed_days from delivery string
    delivery_str = service.basic_delivery if tier == 'basic' else (service.standard_delivery if tier == 'standard' else service.premium_delivery)
    fixed_days = None
    if delivery_str:
        s = delivery_str.lower()
        if 'nửa ngày' in s or 'trong ngày' in s:
            fixed_days = 1
        elif 'theo' not in s:  # Not "theo yêu cầu", "theo lịch"
            import re
            match = re.search(r'(\d+)', s)
            if match:
                fixed_days = int(match.group(1))

    return render_template('book_service.html', service=service, tier=tier, price=price, fixed_days=fixed_days)

# ─── FLOW 2: JOB BOARD ─────────────────────────────────────────────────────────

@app.route('/post-job', methods=['GET', 'POST'])
@login_required
def post_job():
    if request.method == 'POST':
        deadline_str = request.form.get('deadline')
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d').date() if deadline_str else None

        job = Job(
            hirer_id=session['user_id'],
            title=request.form.get('title'),
            description=request.form.get('description'),
            category=request.form.get('category'),
            source_lang=request.form.get('source_lang'),
            target_lang=request.form.get('target_lang'),
            budget_type=request.form.get('budget_type'),
            budget_min=int(request.form.get('budget_min') or 0),
            event_date=request.form.get('event_date', ''),
            event_time_start=request.form.get('event_time_start', ''),
            event_time_end=request.form.get('event_time_end', ''),
            event_location=request.form.get('event_location', ''),
            deadline=deadline
        )
        db.session.add(job)
        db.session.commit()
        flash('Đã đăng việc thành công!', 'success')
        return redirect(url_for('job_list'))
    return render_template('post_job.html', LANGUAGES=LANGUAGES)

@app.route('/jobs')
def job_list():
    lang = request.args.get('lang', '')
    budget = request.args.get('budget', '')
    sort = request.args.get('sort', 'newest')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = Job.query.filter_by(status='open', is_flagged=False)
    if lang:
        query = query.filter(db.or_(Job.source_lang.ilike(f'%{lang}%'), Job.target_lang.ilike(f'%{lang}%')))

    if sort == 'budget_desc':
        query = query.order_by(Job.budget_min.desc())
    else:
        query = query.order_by(Job.created_at.desc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('job_list.html', jobs=pagination.items, pagination=pagination,
                           lang_filter=lang, LANGUAGES=LANGUAGES)

@app.route('/job/<int:job_id>', methods=['GET', 'POST'])
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    if request.method == 'POST':
        if 'user_id' not in session:
            flash('Vui lòng đăng nhập để gửi đề xuất.', 'warning')
            return redirect(url_for('login'))
        proposal = Proposal(
            job_id=job.id,
            translator_id=session['user_id'],
            cover_letter=request.form.get('cover_letter'),
            price=int(request.form.get('price') or 0),
            time_estimate=request.form.get('time_estimate')
        )
        db.session.add(proposal)
        db.session.commit()
        flash('Đề xuất của bạn đã được gửi!', 'success')
        return redirect(url_for('job_detail', job_id=job.id))
    return render_template('job_detail.html', job=job)

# ─── CONTRACT / BUSINESS PROCESS ───────────────────────────────────────────────

@app.route('/accept-proposal/<int:proposal_id>', methods=['POST'])
@login_required
def accept_proposal(proposal_id):
    proposal = Proposal.query.get_or_404(proposal_id)
    job = proposal.job
    if job.hirer_id != session['user_id']:
        flash('Không có quyền.', 'error')
        return redirect(url_for('index'))

    contract = Contract(
        job_id=job.id,
        proposal_id=proposal.id,
        hirer_id=job.hirer_id,
        translator_id=proposal.translator_id,
        agreed_price=proposal.price,
        scheduled_date=job.event_date,
        scheduled_time_start=job.event_time_start,
        scheduled_time_end=job.event_time_end,
        location=job.event_location,
        status='escrow_pending'
    )
    job.status = 'contracted'
    proposal.status = 'accepted'
    db.session.add(contract)
    db.session.commit()
    flash('Đã chấp nhận đề xuất! Vui lòng thanh toán để bắt đầu.', 'success')
    return redirect(url_for('payment_mockup', contract_id=contract.id))

@app.route('/payment-mockup/<int:contract_id>', methods=['GET', 'POST'])
@login_required
def payment_mockup(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    platform_fee = int(contract.agreed_price * 0.10)
    translator_receives = contract.agreed_price - platform_fee
    if request.method == 'POST':
        contract.status = 'in_progress'
        db.session.commit()
        flash('Thanh toán thành công! Tiền đã được giữ trong Escrow an toàn.', 'success')
        return redirect(url_for('transaction_detail', contract_id=contract.id))
    return render_template('payment_mockup.html', contract=contract,
                           platform_fee=platform_fee, translator_receives=translator_receives)

@app.route('/transaction/<int:contract_id>', methods=['GET', 'POST'])
@login_required
def transaction_detail(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if session['user_id'] not in [contract.hirer_id, contract.translator_id]:
        flash('Không có quyền truy cập.', 'error')
        return redirect(url_for('index'))

    if request.method == 'POST' and 'file' in request.files:
        if contract.status == 'in_progress' and session['user_id'] == contract.translator_id:
            file = request.files['file']
            if file.filename != '':
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                db.session.add(Deliverable(contract_id=contract.id, filename=filename, filepath=filename))
                db.session.add(Message(contract_id=contract.id, sender_id=session['user_id'],
                                       content=f'📎 Đã gửi tệp: {filename}'))
                db.session.commit()
                flash('Đã gửi tài liệu thành công.', 'success')

    return render_template('transaction_detail.html', contract=contract)

@app.route('/approve-contract/<int:contract_id>', methods=['POST'])
@login_required
def approve_contract(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if session['user_id'] == contract.hirer_id and contract.status == 'in_progress':
        contract.status = 'completed'
        if contract.job:
            contract.job.status = 'completed'
        prof = TranslatorProfile.query.filter_by(user_id=contract.translator_id).first()
        if prof:
            prof.total_jobs += 1
        db.session.commit()
        flash('Nghiệm thu thành công! Tiền Escrow đã được giải ngân.', 'success')
    return redirect(url_for('transaction_detail', contract_id=contract.id))

@app.route('/submit-review/<int:contract_id>', methods=['POST'])
@login_required
def submit_review(contract_id):
    contract = Contract.query.get_or_404(contract_id)
    if contract.status == 'completed':
        rating = int(request.form.get('rating', 5))
        comment = request.form.get('comment', '')
        reviewee_id = contract.translator_id if session['user_id'] == contract.hirer_id else contract.hirer_id

        existing = Review.query.filter_by(contract_id=contract.id, reviewer_id=session['user_id']).first()
        if existing:
            flash('Bạn đã đánh giá giao dịch này rồi.', 'warning')
            return redirect(url_for('transaction_detail', contract_id=contract.id))

        db.session.add(Review(contract_id=contract.id, reviewer_id=session['user_id'],
                              reviewee_id=reviewee_id, rating=rating, comment=comment))

        if session['user_id'] == contract.hirer_id:
            prof = TranslatorProfile.query.filter_by(user_id=contract.translator_id).first()
            if prof:
                total = (prof.rating * prof.total_reviews) + rating
                prof.total_reviews += 1
                prof.rating = round(total / prof.total_reviews, 1)

        db.session.commit()
        flash('Cảm ơn bạn đã đánh giá!', 'success')
    return redirect(url_for('transaction_detail', contract_id=contract.id))

# ─── CHAT API (CONTRACT) ────────────────────────────────────────────────────────

@app.route('/api/messages/<int:contract_id>')
@login_required
def get_messages(contract_id):
    msgs = Message.query.filter_by(contract_id=contract_id).order_by(Message.created_at.asc()).all()
    return jsonify([{'id': m.id, 'sender_id': m.sender_id, 'sender_name': m.sender.name,
                     'content': m.content, 'time': m.created_at.strftime('%H:%M %d/%m')} for m in msgs])

@app.route('/api/messages/<int:contract_id>', methods=['POST'])
@login_required
def send_message(contract_id):
    content = request.json.get('content', '').strip()
    if content:
        db.session.add(Message(contract_id=contract_id, sender_id=session['user_id'], content=content))
        db.session.commit()
        return jsonify({'status': 'ok'})
    return jsonify({'status': 'error'}), 400

# ─── ADMIN ROUTES ───────────────────────────────────────────────────────────────

@app.route('/admin')
@admin_required
def admin_dashboard():
    stats = {
        'total_users': User.query.filter_by(is_admin=False).count(),
        'total_translators': TranslatorProfile.query.count(),
        'pending_verify': TranslatorProfile.query.filter_by(is_verified=False).count(),
        'open_jobs': Job.query.filter_by(status='open', is_flagged=False).count(),
        'flagged_jobs': Job.query.filter_by(is_flagged=True).count(),
        'active_contracts': Contract.query.filter_by(status='in_progress').count(),
        'completed_contracts': Contract.query.filter_by(status='completed').count(),
    }
    recent_users = User.query.filter_by(is_admin=False).order_by(User.created_at.desc()).limit(5).all()
    recent_jobs = Job.query.order_by(Job.created_at.desc()).limit(5).all()
    return render_template('admin_dashboard.html', stats=stats, recent_users=recent_users, recent_jobs=recent_jobs)

@app.route('/admin/jobs')
@admin_required
def admin_jobs():
    status_filter = request.args.get('status', 'all')
    query = Job.query
    if status_filter == 'flagged':
        query = query.filter_by(is_flagged=True)
    elif status_filter == 'open':
        query = query.filter_by(status='open', is_flagged=False)
    elif status_filter == 'completed':
        query = query.filter_by(status='completed')
    jobs = query.order_by(Job.created_at.desc()).all()
    return render_template('admin_jobs.html', jobs=jobs, status_filter=status_filter)

@app.route('/admin/jobs/<int:job_id>/flag', methods=['POST'])
@admin_required
def admin_flag_job(job_id):
    job = Job.query.get_or_404(job_id)
    job.is_flagged = not job.is_flagged
    db.session.commit()
    action = 'Đã gỡ bỏ' if job.is_flagged else 'Đã khôi phục'
    flash(f'{action} bài đăng "{job.title}".', 'success')
    return redirect(url_for('admin_jobs'))

@app.route('/admin/jobs/<int:job_id>/delete', methods=['POST'])
@admin_required
def admin_delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Đã xoá vĩnh viễn bài đăng.', 'success')
    return redirect(url_for('admin_jobs'))

@app.route('/admin/users')
@admin_required
def admin_users():
    role_filter = request.args.get('role', 'all')
    query = User.query.filter_by(is_admin=False)
    if role_filter == 'hirer':
        query = query.filter_by(role='hirer')
    elif role_filter == 'translator':
        query = query.filter_by(role='translator')
    users = query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users, role_filter=role_filter)

@app.route('/admin/users/<int:user_id>/toggle-active', methods=['POST'])
@admin_required
def admin_toggle_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'kích hoạt' if user.is_active else 'khoá'
    flash(f'Đã {status} tài khoản {user.name}.', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/translators')
@admin_required
def admin_translators():
    show = request.args.get('show', 'pending')
    if show == 'verified':
        profiles = TranslatorProfile.query.filter_by(is_verified=True).all()
    else:
        profiles = TranslatorProfile.query.filter_by(is_verified=False).all()
    return render_template('admin_translators.html', profiles=profiles, show=show)

@app.route('/admin/translators/<int:profile_id>/verify', methods=['POST'])
@admin_required
def admin_verify_translator(profile_id):
    profile = TranslatorProfile.query.get_or_404(profile_id)
    action = request.form.get('action')
    profile.is_verified = (action == 'verify')
    db.session.commit()
    msg = 'Đã xác minh' if profile.is_verified else 'Đã từ chối xác minh'
    flash(f'{msg} hồ sơ {profile.user.name}.', 'success')
    return redirect(url_for('admin_translators'))

if __name__ == '__main__':
    app.run(debug=True)
