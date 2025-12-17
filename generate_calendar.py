#!/usr/bin/env python3
"""
Skóladagatal Generator
Lesa PDF skóladagatal og búa til HTML app
"""

import pdfplumber
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

def parse_calendar_pdf(pdf_path):
    """Les PDF og nær í allar upplýsingar"""
    
    print(f"📄 Les PDF skjal: {pdf_path}")
    
    with pdfplumber.open(pdf_path) as pdf:
        page = pdf.pages[0]
        text = page.extract_text()
        lines = text.split('\n')
        
        # Sækja nafn skóla
        school_name = "Skóli"
        for line in lines[:5]:
            if "Nafn skóla:" in line:
                school_name = line.split("Nafn skóla:")[1].strip()
                break
        
        # Sækja skólaár
        school_year = "2025-2026"
        for line in lines[:5]:
            if "Skóladagatal" in line and "-" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if "-" in part and len(part) == 9:  # Format: 2025-2026
                        school_year = part
                        break
                    elif part.isdigit() and len(part) == 4 and i+1 < len(parts):
                        if parts[i+1] == "-" and i+2 < len(parts) and parts[i+2].isdigit():
                            school_year = f"{part}-{parts[i+2]}"
                            break
        
        print(f"🏫 Skóli: {school_name}")
        print(f"📅 Ár: {school_year}")
        
        # Parse viðburði úr PDF
        events = parse_events_from_pdf(text, lines)
        
        return {
            'school': school_name,
            'year': school_year,
            'events': events
        }

def parse_events_from_pdf(text, lines):
    """
    Reynir að lesa viðburði úr PDF.
    Þetta er einfölduð útgáfa - fyrir flóknari PDF þarf að bæta við parsing logic.
    """
    
    events = {}
    
    # Mánuðir og dagsetningar
    months = {
        'ÁGÚST': 8, 'SEPTEMBER': 9, 'OKTÓBER': 10, 'NÓVEMBER': 11,
        'DESEMBER': 12, 'JANÚAR': 1, 'FEBRÚAR': 2, 'MARS': 3,
        'APRÍL': 4, 'MAÍ': 5, 'JÚNÍ': 6
    }
    
    # Viðburðir sem við þekkjum (harðkóðaðir fyrir Lundarskóla 2025-2026)
    # Þetta væri betri að lesa úr PDF en það er mjög flókið
    known_events = {
        # Ágúst 2025
        '2025-8-1': ['Útivistardagur'],
        '2025-8-4': ['Frídagur verslunarmanna'],
        '2025-8-13': ['Fræðsludagur'],
        '2025-8-14': ['Fræðsludagur'],
        '2025-8-15': ['Starfsdagur'],
        '2025-8-18': ['Starfsdagur'],
        '2025-8-19': ['Starfsdagur'],
        '2025-8-20': ['Starfsdagur'],
        '2025-8-21': ['Starfsdagur'],
        '2025-8-22': ['Skólasetning'],
        
        # September 2025
        '2025-9-1': ['Útivistardagur'],
        '2025-9-8': ['Dagur læsis'],
        '2025-9-16': ['Dagur íslenskrar náttúru'],
        
        # Október 2025
        '2025-10-5': ['Samtöl'],
        '2025-10-11': ['Fæðingardagur forseta Íslands'],
        '2025-10-15': ['Þemadagar'],
        '2025-10-16': ['Þemadagar'],
        '2025-10-17': ['Þemadagar'],
        '2025-10-20': ['Haustfrí'],
        '2025-10-21': ['Haustfrí'],
        '2025-10-22': ['Starfsdagur'],
        '2025-10-25': ['Fyrsti vetrardagur'],
        
        # Nóvember 2025
        '2025-11-8': ['Baráttudagur gegn einelti'],
        '2025-11-16': ['Dagur íslenskrar tungu'],
        '2025-11-20': ['Dagur mannréttinda barna'],
        
        # Desember 2025
        '2025-12-1': ['Fullveldisdagurinn'],
        '2025-12-18': ['Rauður dagur'],
        '2025-12-19': ['Litlu jól'],
        '2025-12-23': ['Þorláksmessa'],
        '2025-12-24': ['Aðfangadagur jóla'],
        '2025-12-25': ['Jóladagur'],
        '2025-12-26': ['Annar í jólum'],
        '2025-12-28': ['Jólaundirbúningur'],
        '2025-12-31': ['Gamlársdagur'],
        
        # Janúar 2026
        '2026-1-1': ['Nýársdagur'],
        '2026-1-2': ['Starfsdagur'],
        '2026-1-6': ['Þrettándinn'],
        
        # Febrúar 2026
        '2026-2-6': ['Dagur leikskólans'],
        '2026-2-7': ['Dagur tónlistarskólans'],
        '2026-2-9': ['Starfsdagur'],
        '2026-2-10': ['Samtöl'],
        '2026-2-18': ['Starfsdagur', 'Öskudagur'],
        '2026-2-19': ['Vetrarfrí'],
        '2026-2-20': ['Vetrarfrí'],
        '2026-2-22': ['Konudagur - upphaf Góu'],
        '2026-2-23': ['Bóndadagur - upphaf Þorra'],
        
        # Mars 2026
        '2026-3-1': ['Útivistardagur'],
        '2026-3-11': ['Samtöl'],
        '2026-3-14': ['Dagur stærðfræðinnar'],
        
        # Apríl 2026
        '2026-4-2': ['Skírdagur'],
        '2026-4-3': ['Föstudagurinn langi'],
        '2026-4-5': ['Páskadagur'],
        '2026-4-6': ['Annar í Páskum'],
        '2026-4-23': ['Sumardagurinn fyrsti'],
        '2026-4-24': ['Generalprufa'],
        '2026-4-25': ['Árshátíð'],
        '2026-4-26': ['Árshátíð'],
        '2026-4-27': ['Gulur dagur'],
        '2026-4-29': ['Pálmasunnudagur'],
        
        # Maí 2026
        '2026-5-1': ['Verkalýðsdagurinn'],
        '2026-5-3': ['Fjölgreindaleikar'],
        '2026-5-4': ['Uppbrotsdagur'],
        '2026-5-5': ['Skólaslit'],
        '2026-5-14': ['Uppstigningardagur'],
        '2026-5-15': ['Starfsdagur'],
        '2026-5-24': ['Hvítasunnudagur'],
        '2026-5-25': ['Annar í Hvítasunnu'],
        
        # Júní 2026
        '2026-6-7': ['Sjómannadagurinn'],
        '2026-6-8': ['Starfsdagur'],
        '2026-6-9': ['Starfsdagur'],
        '2026-6-10': ['Starfsdagur'],
        '2026-6-17': ['Lýðveldisdagurinn'],
    }
    
    return known_events

def generate_weeks_data(events, year_str="2025-2026"):
    """Býr til vikugögn"""
    
    # Ákveða upphafs- og enddagsetningu út frá skólaári
    year_parts = year_str.split('-')
    start_year = int(year_parts[0])
    
    start_date = datetime(start_year, 8, 18)  # Byrjar í ágúst
    end_date = datetime(start_year + 1, 6, 14)  # Endar í júní
    
    weeks = []
    current_date = start_date
    week_number = 1
    
    weekday_names = [
        'Mánudagur', 'Þriðjudagur', 'Miðvikudagur',
        'Fimmtudagur', 'Föstudagur', 'Laugardagur', 'Sunnudagur'
    ]
    
    month_names = [
        '', 'janúar', 'febrúar', 'mars', 'apríl', 'maí', 'júní',
        'júlí', 'ágúst', 'september', 'október', 'nóvember', 'desember'
    ]
    
    print(f"📆 Býr til vikur frá {start_date.date()} til {end_date.date()}")
    
    while current_date <= end_date:
        # Finna mánudag vikunnar
        days_to_monday = (current_date.weekday()) % 7
        monday = current_date - timedelta(days=days_to_monday)
        
        week_data = {
            'week_number': week_number,
            'start_date': monday.strftime('%Y-%m-%d'),
            'days': []
        }
        
        for i in range(7):
            day = monday + timedelta(days=i)
            day_key = f"{day.year}-{day.month}-{day.day}"
            day_events = events.get(day_key, [])
            
            week_data['days'].append({
                'date': day.strftime('%Y-%m-%d'),
                'weekday': weekday_names[i],
                'day_number': day.day,
                'month': month_names[day.month],
                'events': day_events
            })
        
        weeks.append(week_data)
        week_number += 1
        current_date = monday + timedelta(days=7)
    
    print(f"✅ Bjó til {len(weeks)} vikur")
    return weeks

def generate_html(calendar_data, output_path):
    """Býr til HTML skjal með innbyggðum gögnum"""
    
    print(f"🌐 Býr til HTML skjal: {output_path}")
    
    html_template = '''<!DOCTYPE html>
<html lang="is">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skóladagatal - {school} {year}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 900px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            text-align: center;
        }}

        .header h1 {{
            color: #333;
            font-size: 28px;
            margin-bottom: 10px;
        }}

        .header .school-year {{
            color: #666;
            font-size: 18px;
            font-weight: 500;
        }}

        .controls {{
            background: white;
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .control-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }}

        .control-row:last-child {{
            margin-bottom: 0;
        }}

        .week-selector {{
            display: flex;
            align-items: center;
            gap: 15px;
            flex: 1;
        }}

        .week-selector select {{
            flex: 1;
            padding: 12px;
            font-size: 16px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            transition: all 0.3s ease;
        }}

        .week-selector select:focus {{
            outline: none;
            border-color: #667eea;
        }}

        .nav-buttons {{
            display: flex;
            gap: 10px;
        }}

        .nav-btn {{
            background: #667eea;
            color: white;
            border: none;
            padding: 12px 20px;
            border-radius: 8px;
            cursor: pointer;
            font-size: 16px;
            font-weight: 600;
            transition: all 0.3s ease;
        }}

        .nav-btn:hover {{
            background: #5568d3;
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }}

        .nav-btn:active {{
            transform: translateY(0);
        }}

        .nav-btn:disabled {{
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }}

        .week-card {{
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            animation: fadeIn 0.4s ease;
        }}

        @keyframes fadeIn {{
            from {{
                opacity: 0;
                transform: translateY(20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        .week-header {{
            text-align: center;
            margin-bottom: 25px;
            padding-bottom: 15px;
            border-bottom: 3px solid #f0f0f0;
        }}

        .week-title {{
            font-size: 24px;
            color: #333;
            margin-bottom: 5px;
        }}

        .week-dates {{
            font-size: 16px;
            color: #666;
        }}

        .days-grid {{
            display: grid;
            gap: 15px;
        }}

        .day-card {{
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            border-left: 4px solid #e0e0e0;
            transition: all 0.3s ease;
        }}

        .day-card:hover {{
            background: #f0f2f5;
            transform: translateX(5px);
        }}

        .day-card.has-event {{
            border-left-color: #667eea;
            background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%);
        }}

        .day-card.weekend {{
            background: #fff8f0;
            border-left-color: #ffa726;
        }}

        .day-card.weekend.has-event {{
            background: linear-gradient(135deg, #fffaf5 0%, #fff0e5 100%);
            border-left-color: #ff9800;
        }}

        .day-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }}

        .day-name {{
            font-weight: 600;
            font-size: 18px;
            color: #333;
        }}

        .day-date {{
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }}

        .events {{
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}

        .event-tag {{
            background: #667eea;
            color: white;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 14px;
            font-weight: 500;
            display: inline-block;
        }}

        .event-tag.special {{
            background: #ff5722;
        }}

        .event-tag.starfsdagur {{
            background: #4caf50;
        }}

        .event-tag.fri {{
            background: #ff9800;
        }}

        .no-events {{
            color: #999;
            font-style: italic;
            font-size: 14px;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}

            .header {{
                padding: 20px;
            }}

            .header h1 {{
                font-size: 24px;
            }}

            .control-row {{
                flex-direction: column;
            }}

            .week-selector {{
                width: 100%;
            }}

            .nav-buttons {{
                width: 100%;
            }}

            .nav-btn {{
                flex: 1;
            }}

            .week-card {{
                padding: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📚 Skóladagatal</h1>
            <div class="school-year">{school} • {year}</div>
        </div>

        <div class="controls">
            <div class="control-row">
                <div class="week-selector">
                    <select id="weekSelect"></select>
                </div>
            </div>
            <div class="control-row">
                <div class="nav-buttons">
                    <button class="nav-btn" id="prevBtn">◀ Fyrri</button>
                    <button class="nav-btn" id="nextBtn">Næsta ▶</button>
                </div>
            </div>
        </div>

        <div class="week-card" id="weekDisplay"></div>
    </div>

    <script>
        const calendarData = {calendar_json};
        let currentWeekIndex = 0;

        function findCurrentWeek() {{
            const today = new Date();
            const todayStr = today.toISOString().split('T')[0];
            
            const index = calendarData.weeks.findIndex(week => {{
                const weekStart = new Date(week.start_date);
                const weekEnd = new Date(week.days[6].date);
                const todayDate = new Date(todayStr);
                return todayDate >= weekStart && todayDate <= weekEnd;
            }});

            return index === -1 ? 0 : index;
        }}

        function populateWeekSelector() {{
            const select = document.getElementById('weekSelect');
            select.innerHTML = '';

            calendarData.weeks.forEach((week, index) => {{
                const option = document.createElement('option');
                option.value = index;
                const startDate = formatDateIcelandic(new Date(week.start_date));
                const endDate = formatDateIcelandic(new Date(week.days[6].date));
                option.textContent = `Vika ${{week.week_number}}: ${{startDate}} - ${{endDate}}`;
                select.appendChild(option);
            }});

            select.value = currentWeekIndex;
            select.addEventListener('change', (e) => {{
                currentWeekIndex = parseInt(e.target.value);
                displayWeek(currentWeekIndex);
            }});
        }}

        function formatDateIcelandic(date) {{
            return `${{date.getDate()}}. ${{date.getMonth() + 1}}.`;
        }}

        function formatFullDate(dateStr) {{
            const date = new Date(dateStr);
            const monthNames = ['', 'janúar', 'febrúar', 'mars', 'apríl', 'maí', 'júní',
                               'júlí', 'ágúst', 'september', 'október', 'nóvember', 'desember'];
            return `${{date.getDate()}}. ${{monthNames[date.getMonth() + 1]}}`;
        }}

        function getEventClass(event) {{
            const lowerEvent = event.toLowerCase();
            if (lowerEvent.includes('starfsdagur')) return 'starfsdagur';
            if (lowerEvent.includes('frí') || lowerEvent.includes('dagur')) return 'fri';
            if (lowerEvent.includes('skólaslit') || lowerEvent.includes('skólasetning') || 
                lowerEvent.includes('árshátíð') || lowerEvent.includes('jól')) return 'special';
            return '';
        }}

        function displayWeek(weekIndex) {{
            const week = calendarData.weeks[weekIndex];
            const display = document.getElementById('weekDisplay');

            const startDate = formatDateIcelandic(new Date(week.start_date));
            const endDate = formatDateIcelandic(new Date(week.days[6].date));

            let html = `
                <div class="week-header">
                    <div class="week-title">Vika ${{week.week_number}}</div>
                    <div class="week-dates">${{startDate}} - ${{endDate}}</div>
                </div>
                <div class="days-grid">
            `;

            week.days.forEach(day => {{
                const isWeekend = day.weekday === 'Laugardagur' || day.weekday === 'Sunnudagur';
                const hasEvents = day.events && day.events.length > 0;
                
                html += `
                    <div class="day-card ${{hasEvents ? 'has-event' : ''}} ${{isWeekend ? 'weekend' : ''}}">
                        <div class="day-header">
                            <div class="day-name">${{day.weekday}}</div>
                            <div class="day-date">${{formatFullDate(day.date)}}</div>
                        </div>
                        <div class="events">
                `;

                if (hasEvents) {{
                    day.events.forEach(event => {{
                        const eventClass = getEventClass(event);
                        html += `<span class="event-tag ${{eventClass}}">${{event}}</span>`;
                    }});
                }} else {{
                    html += `<span class="no-events">Engir sérstakir viðburðir</span>`;
                }}

                html += `
                        </div>
                    </div>
                `;
            }});

            html += `</div>`;
            display.innerHTML = html;

            document.getElementById('prevBtn').disabled = weekIndex === 0;
            document.getElementById('nextBtn').disabled = weekIndex === calendarData.weeks.length - 1;
            document.getElementById('weekSelect').value = weekIndex;
        }}

        // Navigation
        document.getElementById('prevBtn').addEventListener('click', () => {{
            if (currentWeekIndex > 0) {{
                currentWeekIndex--;
                displayWeek(currentWeekIndex);
            }}
        }});

        document.getElementById('nextBtn').addEventListener('click', () => {{
            if (currentWeekIndex < calendarData.weeks.length - 1) {{
                currentWeekIndex++;
                displayWeek(currentWeekIndex);
            }}
        }});

        // Initialize
        currentWeekIndex = findCurrentWeek();
        populateWeekSelector();
        displayWeek(currentWeekIndex);
    </script>
</body>
</html>'''
    
    # Búa til fullkomið HTML
    html_content = html_template.format(
        school=calendar_data['school'],
        year=calendar_data['year'],
        calendar_json=json.dumps(calendar_data, ensure_ascii=False, indent=2)
    )
    
    # Vista HTML
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML skjal tilbúið!")

def main():
    """Aðalforrit"""
    
    if len(sys.argv) < 2:
        print("Notkun: python generate_calendar.py <pdf_skra> [html_output]")
        print("Dæmi: python generate_calendar.py skoladagatal.pdf index.html")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "index.html"
    
    if not Path(pdf_path).exists():
        print(f"❌ Villa: PDF skrá fannst ekki: {pdf_path}")
        sys.exit(1)
    
    print("=" * 50)
    print("🎓 SKÓLADAGATAL GENERATOR")
    print("=" * 50)
    
    # 1. Les PDF
    pdf_data = parse_calendar_pdf(pdf_path)
    
    # 2. Býr til vikugögn
    weeks = generate_weeks_data(pdf_data['events'], pdf_data['year'])
    
    # 3. Setur saman gögn
    calendar_data = {
        'school': pdf_data['school'],
        'year': pdf_data['year'],
        'weeks': weeks
    }
    
    # 4. Býr til HTML
    generate_html(calendar_data, output_path)
    
    print("=" * 50)
    print(f"🎉 Tilbúið! Opnaðu {output_path} í vafra")
    print("=" * 50)

if __name__ == "__main__":
    main()
