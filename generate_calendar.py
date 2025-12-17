#!/usr/bin/env python3
"""
Skóladagatal Generator - Les allt úr PDF (LAGAÐ)
"""

import pdfplumber
import json
import sys
import re
from datetime import datetime, timedelta
from pathlib import Path

def parse_calendar_pdf(pdf_path):
    """Les PDF og nær í ALLAR upplýsingar úr skjalinu"""
    
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
        school_year = None
        for line in lines[:10]:
            if "Skóladagatal" in line or any(char.isdigit() for char in line):
                match = re.search(r'(\d{4})\s*-\s*(\d{4})', line)
                if match:
                    school_year = f"{match.group(1)}-{match.group(2)}"
                    break
        
        if not school_year:
            print("⚠️ Gat ekki fundið skólaár í PDF, nota 2025-2026 sem sjálfgefið")
            school_year = "2025-2026"
        
        print(f"🏫 Skóli: {school_name}")
        print(f"📅 Ár: {school_year}")
        
        # Parse viðburði úr PDF
        events = parse_events_from_calendar_lines(lines, school_year)
        
        return {
            'school': school_name,
            'year': school_year,
            'events': events
        }

def parse_events_from_calendar_lines(lines, school_year):
    """Les viðburði beint úr dagatals-línunum í PDF með lagaðri röðun"""
    
    events = {}
    
    # Mánuðir í röð
    months = ['ÁGÚST', 'SEPTEMBER', 'OKTÓBER', 'NÓVEMBER', 'DESEMBER', 
              'JANÚAR', 'FEBRÚAR', 'MARS', 'APRÍL', 'MAÍ', 'JÚNÍ']
    month_numbers = [8, 9, 10, 11, 12, 1, 2, 3, 4, 5, 6]
    
    # Finna mánuða-línuna
    month_line_idx = -1
    for i, line in enumerate(lines):
        if 'ÁGÚST' in line and 'SEPTEMBER' in line:
            month_line_idx = i
            break
    
    if month_line_idx == -1:
        print("⚠️  Gat ekki fundið mánuðalínu")
        return events
    
    print(f"📆 Les viðburði úr PDF...")
    
    # Ákvarða ár fyrir hvern mánuð
    year_parts = school_year.split('-')
    start_year = int(year_parts[0])
    
    def get_year_for_month(month_num):
        return start_year if month_num >= 8 else start_year + 1
    
    # Fara í gegnum hverja dagatals-línu
    event_count = 0
    for line_idx in range(month_line_idx + 1, len(lines)):
        line = lines[line_idx]
        
        # Stoppa ef við komum að textanum neðst
        if 'Samkvæmt' in line or 'Sérstakir' in line or 'Starfsdagar' in line:
            break
        
        if not line.strip():
            continue
        
        # Athuga hvort lína byrji á dagnúmeri
        parts = line.split()
        if not parts:
            continue
            
        first_part = parts[0].rstrip('SMÞFLsmþfl')
        if not first_part.isdigit():
            continue
            
        day_num = int(first_part)
        
        # Skipta línunni á dagnúmerinu til að fá hluta fyrir hvern mánuð
        # Dæmi: "28F 28S 28Þ 28F Jólaundirbúningur 28S 28M..."
        # Split gefur okkur: ['', 'S ', 'Þ ', 'F Jólaundirbúningur ', 'S ', 'M ', ...]
        split_parts = re.split(rf'\b{day_num}\s*[SMÞFL]?\s*', line)
        
        # Fyrsti hlutinn er fyrir fyrsta dagnúmerið, svo við sleppum honum
        month_parts = split_parts[1:]
        
        # Fara í gegnum hvern mánuð
        for month_idx in range(min(len(month_parts), len(months))):
            part = month_parts[month_idx]
            
            # Hreinsa burt næsta dagnúmer og allt eftir það
            clean_text = re.sub(r'\s*\d+\s*[SMÞFL]?.*$', '', part).strip()
            
            # Athuga hvort það sé viðburður hér
            if clean_text and len(clean_text) > 1:
                # Athuga að þetta séu ekki bara vikudagsstafir
                if not re.match(r'^[SMÞFL\s]*$', clean_text):
                    month_num = month_numbers[month_idx]
                    year = get_year_for_month(month_num)
                    date_key = f"{year}-{month_num}-{day_num}"
                    
                    # Skipta upp ef margir viðburðir (með /)
                    if '/' in clean_text:
                        event_list = [e.strip() for e in clean_text.split('/')]
                    else:
                        event_list = [clean_text]
                    
                    if date_key not in events:
                        events[date_key] = []
                    
                    for event in event_list:
                        if event and event not in events[date_key]:
                            events[date_key].append(event)
                            event_count += 1
    
    print(f"✅ Fann {event_count} viðburði")
    
    # Sýna dæmi
    if events:
        print("📋 Dæmi um viðburði:")
        count = 0
        for date in sorted(events.keys()):
            if count < 5:
                print(f"   {date}: {', '.join(events[date])}")
                count += 1
    
    return events

def generate_weeks_data(events, year_str):
    """Býr til vikugögn byggð á raunverulegum viðburðum"""
    
    if not events:
        print("⚠️ Engir viðburðir fundnir, nota sjálfgefnar dagsetningar")
        year_parts = year_str.split('-')
        start_year = int(year_parts[0])
        start_date = datetime(start_year, 8, 18)
        end_date = datetime(start_year + 1, 6, 14)
    else:
        # Finna fyrsta og síðasta dag með viðburði
        all_dates = []
        for date_str in events.keys():
            try:
                parts = date_str.split('-')
                year, month, day = int(parts[0]), int(parts[1]), int(parts[2])
                all_dates.append(datetime(year, month, day))
            except (ValueError, IndexError) as e:
                print(f"⚠️ Sleppti ógildri dagsetningu: {date_str}")
                continue
        
        if not all_dates:
            print("⚠️ Engar gildar dagsetningar, nota sjálfgefnar")
            year_parts = year_str.split('-')
            start_year = int(year_parts[0])
            start_date = datetime(start_year, 8, 18)
            end_date = datetime(start_year + 1, 6, 14)
        else:
            min_date = min(all_dates)
            max_date = max(all_dates)
            
            # Víkka tímabilið lítillega til að fá allar skólavikur
            # Fara aftur í næsta mánudag fyrir min_date
            days_to_monday = min_date.weekday()
            start_date = min_date - timedelta(days=days_to_monday)
            
            # Fara fram að næsta sunnudegi eftir max_date
            days_to_sunday = 6 - max_date.weekday()
            end_date = max_date + timedelta(days=days_to_sunday)
            
            print(f"📆 Dagatal spannar: {min_date.date()} til {max_date.date()}")
            print(f"📆 Vikur búnar til: {start_date.date()} til {end_date.date()}")
    
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
    
    while current_date <= end_date:
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
    """Býr til HTML skjal"""
    
    print(f"🌐 Býr til HTML skjal: {output_path}")
    
    html_template = open('/home/claude/html_template.txt', 'r').read() if Path('/home/claude/html_template.txt').exists() else '''<!DOCTYPE html>
<html lang="is">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Skóladagatal - {school} {year}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        .header {{ background: white; border-radius: 15px; padding: 25px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); text-align: center; }}
        .header h1 {{ color: #333; font-size: 28px; margin-bottom: 10px; }}
        .header .school-year {{ color: #666; font-size: 18px; font-weight: 500; }}
        .controls {{ background: white; border-radius: 15px; padding: 20px; margin-bottom: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .control-row {{ display: flex; justify-content: space-between; align-items: center; gap: 15px; margin-bottom: 15px; }}
        .control-row:last-child {{ margin-bottom: 0; }}
        .week-selector {{ display: flex; align-items: center; gap: 15px; flex: 1; }}
        .week-selector select {{ flex: 1; padding: 12px; font-size: 16px; border: 2px solid #e0e0e0; border-radius: 8px; background: white; cursor: pointer; }}
        .nav-buttons {{ display: flex; gap: 10px; }}
        .nav-btn {{ background: #667eea; color: white; border: none; padding: 12px 20px; border-radius: 8px; cursor: pointer; font-size: 16px; font-weight: 600; transition: all 0.3s ease; }}
        .nav-btn:hover {{ background: #5568d3; transform: translateY(-2px); }}
        .nav-btn:disabled {{ background: #ccc; cursor: not-allowed; }}
        .week-card {{ background: white; border-radius: 15px; padding: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .week-header {{ text-align: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 3px solid #f0f0f0; }}
        .week-title {{ font-size: 24px; color: #333; margin-bottom: 5px; }}
        .week-dates {{ font-size: 16px; color: #666; }}
        .days-grid {{ display: grid; gap: 15px; }}
        .day-card {{ background: #f8f9fa; border-radius: 10px; padding: 15px; border-left: 4px solid #e0e0e0; transition: all 0.3s ease; }}
        .day-card:hover {{ background: #f0f2f5; transform: translateX(5px); }}
        .day-card.has-event {{ border-left-color: #667eea; background: linear-gradient(135deg, #f8f9ff 0%, #f0f2ff 100%); }}
        .day-card.weekend {{ background: #fff8f0; border-left-color: #ffa726; }}
        .day-card.weekend.has-event {{ background: linear-gradient(135deg, #fffaf5 0%, #fff0e5 100%); border-left-color: #ff9800; }}
        .day-header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }}
        .day-name {{ font-weight: 600; font-size: 18px; color: #333; }}
        .day-date {{ font-size: 14px; color: #666; font-weight: 500; }}
        .events {{ display: flex; flex-direction: column; gap: 8px; }}
        .event-tag {{ background: #667eea; color: white; padding: 8px 12px; border-radius: 6px; font-size: 14px; font-weight: 500; }}
        .event-tag.special {{ background: #ff5722; }}
        .event-tag.starfsdagur {{ background: #4caf50; }}
        .event-tag.fri {{ background: #ff9800; }}
        .no-events {{ color: #999; font-style: italic; font-size: 14px; }}
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
                <div class="week-selector"><select id="weekSelect"></select></div>
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
        function formatDateIcelandic(date) {{ return `${{date.getDate()}}. ${{date.getMonth() + 1}}.`; }}
        function formatFullDate(dateStr) {{
            const date = new Date(dateStr);
            const monthNames = ['', 'janúar', 'febrúar', 'mars', 'apríl', 'maí', 'júní', 'júlí', 'ágúst', 'september', 'október', 'nóvember', 'desember'];
            return `${{date.getDate()}}. ${{monthNames[date.getMonth() + 1]}}`;
        }}
        function getEventClass(event) {{
            const lowerEvent = event.toLowerCase();
            if (lowerEvent.includes('starfsdagur')) return 'starfsdagur';
            if (lowerEvent.includes('frí') || lowerEvent.includes('dagur')) return 'fri';
            if (lowerEvent.includes('skólaslit') || lowerEvent.includes('skólasetning') || lowerEvent.includes('árshátíð') || lowerEvent.includes('jól')) return 'special';
            return '';
        }}
        function displayWeek(weekIndex) {{
            const week = calendarData.weeks[weekIndex];
            const display = document.getElementById('weekDisplay');
            const startDate = formatDateIcelandic(new Date(week.start_date));
            const endDate = formatDateIcelandic(new Date(week.days[6].date));
            let html = `<div class="week-header"><div class="week-title">Vika ${{week.week_number}}</div><div class="week-dates">${{startDate}} - ${{endDate}}</div></div><div class="days-grid">`;
            week.days.forEach(day => {{
                const isWeekend = day.weekday === 'Laugardagur' || day.weekday === 'Sunnudagur';
                const hasEvents = day.events && day.events.length > 0;
                html += `<div class="day-card ${{hasEvents ? 'has-event' : ''}} ${{isWeekend ? 'weekend' : ''}}"><div class="day-header"><div class="day-name">${{day.weekday}}</div><div class="day-date">${{formatFullDate(day.date)}}</div></div><div class="events">`;
                if (hasEvents) {{
                    day.events.forEach(event => {{
                        const eventClass = getEventClass(event);
                        html += `<span class="event-tag ${{eventClass}}">${{event}}</span>`;
                    }});
                }} else {{
                    html += `<span class="no-events">Engir sérstakir viðburðir</span>`;
                }}
                html += `</div></div>`;
            }});
            html += `</div>`;
            display.innerHTML = html;
            document.getElementById('prevBtn').disabled = weekIndex === 0;
            document.getElementById('nextBtn').disabled = weekIndex === calendarData.weeks.length - 1;
            document.getElementById('weekSelect').value = weekIndex;
        }}
        document.getElementById('prevBtn').addEventListener('click', () => {{ if (currentWeekIndex > 0) {{ currentWeekIndex--; displayWeek(currentWeekIndex); }} }});
        document.getElementById('nextBtn').addEventListener('click', () => {{ if (currentWeekIndex < calendarData.weeks.length - 1) {{ currentWeekIndex++; displayWeek(currentWeekIndex); }} }});
        currentWeekIndex = findCurrentWeek();
        populateWeekSelector();
        displayWeek(currentWeekIndex);
    </script>
</body>
</html>'''
    
    html_content = html_template.format(
        school=calendar_data['school'],
        year=calendar_data['year'],
        calendar_json=json.dumps(calendar_data, ensure_ascii=False, indent=2)
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"✅ HTML skjal tilbúið!")

def main():
    if len(sys.argv) < 2:
        print("Notkun: python generate_calendar.py <pdf_skra> [html_output]")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else "index.html"
    
    if not Path(pdf_path).exists():
        print(f"❌ Villa: PDF skrá fannst ekki: {pdf_path}")
        sys.exit(1)
    
    print("=" * 50)
    print("🎓 SKÓLADAGATAL GENERATOR")
    print("=" * 50)
    
    pdf_data = parse_calendar_pdf(pdf_path)
    weeks = generate_weeks_data(pdf_data['events'], pdf_data['year'])
    
    calendar_data = {
        'school': pdf_data['school'],
        'year': pdf_data['year'],
        'weeks': weeks
    }
    
    generate_html(calendar_data, output_path)
    
    print("=" * 50)
    print(f"🎉 Tilbúið! Opnaðu {output_path} í vafra")
    print("=" * 50)

if __name__ == "__main__":
    main()
