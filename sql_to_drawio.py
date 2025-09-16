#!/usr/bin/env python3
"""
Конвертер SQL в Draw.io диаграмму в нотации Чена
Использование: python sql_to_drawio.py input.sql output.drawio
"""

import re
import sys
import argparse

def parse_sql_file(sql_file):
    """Парсит SQL файл и извлекает таблицы, атрибуты и связи"""
    
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Удаляем комментарии для упрощения парсинга
    sql = re.sub(r'--.*?$', '', sql, flags=re.MULTILINE)
    
    tables = {}
    relationships = []
    
    # Парсим CREATE TABLE statements
    create_pattern = r'CREATE TABLE (?:IF NOT EXISTS )?["\']?(\w+)["\']?\s*\((.*?)\);'
    create_matches = re.finditer(create_pattern, sql, re.IGNORECASE | re.DOTALL)
    
    for match in create_matches:
        table_name = match.group(1)
        table_content = match.group(2)
        
        # Извлекаем атрибуты (колонки)
        attributes = []
        lines = table_content.split(',')
        
        for line in lines:
            line = line.strip()
            # Пропускаем CONSTRAINT, PRIMARY KEY, FOREIGN KEY
            if any(keyword in line.upper() for keyword in ['CONSTRAINT', 'PRIMARY KEY', 'FOREIGN KEY', 'UNIQUE']):
                continue
            
            # Ищем шаблон: имя_колонки тип_данных [дополнительно]
            column_match = re.match(r'^(\w+)\s+([\w\(\)]+)', line)
            if column_match:
                col_name = column_match.group(1)
                col_type = column_match.group(2)
                attributes.append({'name': col_name, 'type': col_type})
        
        tables[table_name] = attributes
        print(f"📋 Таблица: {table_name} ({len(attributes)} атрибутов)")
    
    # Парсим отдельно ALTER TABLE statements для связей
    alter_pattern = r'ALTER TABLE (\w+)\s+ADD CONSTRAINT [\w_]+ FOREIGN KEY \((\w+)\) REFERENCES (\w+)\((\w+)\)'
    alter_matches = re.finditer(alter_pattern, sql, re.IGNORECASE)
    
    for i, match in enumerate(alter_matches):
        from_table = match.group(1)
        from_column = match.group(2)
        to_table = match.group(3)
        to_column = match.group(4)
        
        relationships.append({
            'id': f"rel_{i}",
            'from_table': from_table,
            'to_table': to_table,
            'description': get_relationship_description(from_table, to_table)
        })
        
        print(f"🔗 Связь: {from_table} -> {to_table}")
    
    return tables, relationships

def get_relationship_description(from_table, to_table):
    """Генерирует описание связи на основе названий таблиц"""
    """ тут вручную"""
    relationships_map = {
        ('documents', 'clients'): 'принадлежит',
        ('credit_history', 'clients'): 'имеет',
        ('credit_applications', 'clients'): 'подает',
        ('credit_applications', 'employees'): 'обрабатывает',
        ('credit_applications', 'loan_products'): 'запрашивает',
        ('application_documents', 'credit_applications'): 'содержит',
        ('application_documents', 'documents'): 'использует',
        ('accounts', 'clients'): 'открывает',
        ('credit_contracts', 'credit_applications'): 'создает',
        ('credit_contracts', 'loan_products'): 'основан на',
        ('credit_contracts', 'accounts'): 'привязан к',
        ('payment_schedule', 'credit_contracts'): 'имеет',
        ('payments', 'payment_schedule'): 'погашает',
        ('payments', 'accounts'): 'зачисляется на'
    }
    
    return relationships_map.get((from_table, to_table), 'связан с')

def generate_chen_diagram(tables, relationships):
    """Генерирует диаграмму в нотации Чена"""
    
    xml_content = []
    entity_positions = {}
    used_ids = set()
    
    # Генерация уникального ID
    def get_unique_id(base_id):
        counter = 1
        new_id = base_id
        while new_id in used_ids:
            new_id = f"{base_id}_{counter}"
            counter += 1
        used_ids.add(new_id)
        return new_id
    
    # Позиционирование сущностей (прямоугольники)
    x, y = 50, 50
    for table_name, attributes in tables.items():
        entity_id = get_unique_id(f"entity_{table_name}")
        entity_positions[table_name] = (x, y)
        
        # Сущность (прямоугольник)
        xml_content.append(f'''
        <mxCell id="{entity_id}" value="{table_name}" style="shape=rectangle;whiteSpace=wrap;html=1;rounded=0;fillColor=#ffffff;strokeColor=#000000;strokeWidth=2;" vertex="1" parent="1">
            <mxGeometry x="{x}" y="{y}" width="120" height="40" as="geometry"/>
        </mxCell>''')
        
        # Атрибуты (овалы)
        attr_y = y + 60
        for attr in attributes:
            attr_id = get_unique_id(f"attr_{table_name}_{attr['name']}")
            
            xml_content.append(f'''
            <mxCell id="{attr_id}" value="{attr['name']}" style="shape=ellipse;whiteSpace=wrap;html=1;fillColor=#f5f5f5;strokeColor=#666666;" vertex="1" parent="1">
                <mxGeometry x="{x}" y="{attr_y}" width="100" height="30" as="geometry"/>
            </mxCell>''')
            
            # Связь атрибута с сущностью
            conn_id = get_unique_id(f"conn_{attr_id}")
            xml_content.append(f'''
            <mxCell id="{conn_id}" style="endArrow=none;html=1;rounded=0;strokeWidth=1;strokeColor=#666666;dashed=1;" edge="1" parent="1" source="{attr_id}" target="{entity_id}">
                <mxGeometry width="50" height="50" relative="1" as="geometry"/>
            </mxCell>''')
            
            attr_y += 40
        
        x += 250
        if x > 1000:
            x = 50
            y += 300
    
    # Позиционирование связей (ромбы)
    for rel in relationships:
        if rel['from_table'] not in entity_positions or rel['to_table'] not in entity_positions:
            continue
        
        from_x, from_y = entity_positions[rel['from_table']]
        to_x, to_y = entity_positions[rel['to_table']]
        
        # Позиция ромба посередине между сущностями
        rel_x = (from_x + to_x) // 2
        rel_y = (from_y + to_y) // 2
        
        # Ромб связи с текстом
        rel_id = get_unique_id(rel['id'])
        xml_content.append(f'''
        <mxCell id="{rel_id}" value="{rel['description']}" style="shape=rhombus;whiteSpace=wrap;html=1;fillColor=#e6f3ff;strokeColor=#0066cc;strokeWidth=2;fontSize=12;" vertex="1" parent="1">
            <mxGeometry x="{rel_x}" y="{rel_y}" width="80" height="40" as="geometry"/>
        </mxCell>''')
        
        # Простая линия от исходной таблицы к ромбу (без стрелок)
        from_entity_id = f"entity_{rel['from_table']}"
        conn_from_id = get_unique_id(f"conn_from_{rel_id}")
        xml_content.append(f'''
        <mxCell id="{conn_from_id}" style="endArrow=none;html=1;rounded=0;strokeWidth=2;strokeColor=#0066cc;" edge="1" parent="1" source="{from_entity_id}" target="{rel_id}">
            <mxGeometry width="50" height="50" relative="1" as="geometry"/>
        </mxCell>''')
        
        # Простая линия от ромба к целевой таблице (без стрелок)
        to_entity_id = f"entity_{rel['to_table']}"
        conn_to_id = get_unique_id(f"conn_to_{rel_id}")
        xml_content.append(f'''
        <mxCell id="{conn_to_id}" style="endArrow=none;html=1;rounded=0;strokeWidth=2;strokeColor=#0066cc;" edge="1" parent="1" source="{rel_id}" target="{to_entity_id}">
            <mxGeometry width="50" height="50" relative="1" as="geometry"/>
        </mxCell>''')
    
    return f'''<mxfile>
    <diagram>
        <mxGraphModel dx="2500" dy="2500">
            <root>
                <mxCell id="0"/>
                <mxCell id="1" parent="0"/>
                {''.join(xml_content)}
            </root>
        </mxGraphModel>
    </diagram>
</mxfile>'''

def sql_to_drawio(sql_file, output_file):
    """Конвертирует SQL в Draw.io диаграмму"""
    
    try:
        tables, relationships = parse_sql_file(sql_file)
        
        if not tables:
            print("❌ Не найдено таблиц в SQL файле")
            return False
        
        drawio_content = generate_chen_diagram(tables, relationships)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(drawio_content)
        
        print(f"✅ Готово! Создан файл: {output_file}")
        print(f"📊 Сущностей: {len(tables)}, Связей: {len(relationships)}")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Основная функция с обработкой аргументов"""
    
    parser = argparse.ArgumentParser(description='Конвертер SQL в Draw.io диаграмму (нотация Чена)')
    parser.add_argument('input', help='Входной SQL файл')
    parser.add_argument('output', help='Выходной Draw.io файл')
    
    args = parser.parse_args()
    
    print("🔄 Конвертация SQL в Draw.io (нотация Чена)")
    print("=" * 50)
    
    success = sql_to_drawio(args.input, args.output)
    
    if success:
        print("🎉 Конвертация завершена успешно!")
        print("💡 Откройте файл в VS Code с расширением Draw.io")
    else:
        print("💥 Конвертация завершена с ошибками!")
        sys.exit(1)

if __name__ == "__main__":
    main()