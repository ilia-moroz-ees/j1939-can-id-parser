import argparse

def parse_j1939_id(can_id):
    """Parse J1939 CAN ID into its components"""
    can_id = int(can_id)
    priority = (can_id >> 26) & 0x7
    reserved = (can_id >> 25) & 0x1
    data_page = (can_id >> 24) & 0x1
    pdu_format = (can_id >> 16) & 0xFF
    pdu_specific = (can_id >> 8) & 0xFF
    source_address = can_id & 0xFF
    
    # Determine PGN
    if pdu_format < 240:
        # PDU1 format, destination specific
        pgn = (data_page << 16) | (pdu_format << 8)
    else:
        # PDU2 format, broadcast
        pgn = (data_page << 16) | (pdu_format << 8) | pdu_specific
    
    return {
        'priority': priority,
        'reserved': reserved,
        'data_page': data_page,
        'pdu_format': pdu_format,
        'pdu_specific': pdu_specific,
        'source_address': source_address,
        'pgn': pgn
    }

def build_j1939_id(priority, pgn, source_address, reserved=0):
    """Build J1939 CAN ID from components"""
    priority = int(priority) & 0x7
    reserved = int(reserved) & 0x1
    source_address = int(source_address) & 0xFF
    pgn = int(pgn)
    
    # Extract PGN components
    data_page = (pgn >> 16) & 0x1
    pdu_format = (pgn >> 8) & 0xFF
    pdu_specific = pgn & 0xFF
    
    # For PDU1 format (pdu_format < 240), pdu_specific is actually the destination address
    # but in the CAN ID it occupies the same bits as PDU specific in PDU2 format
    can_id = (priority << 26) | (reserved << 25) | (data_page << 24) | (pdu_format << 16)
    can_id |= (pdu_specific << 8) | source_address
    
    return can_id

def main():
    parser = argparse.ArgumentParser(
        description='J1939 CAN ID Parser and Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''Examples:
  Parse a CAN ID:
    python j1939_tool.py --parse 0x18FEF100
  
  Generate a CAN ID from components:
    python j1939_tool.py --generate --priority 6 --pgn 65262 --source-address 0x00
''')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--parse', metavar='CAN_ID', help='Parse a J1939 CAN ID (decimal or hex)')
    group.add_argument('--generate', action='store_true', help='Generate a J1939 CAN ID from components')
    
    # Generation arguments
    parser.add_argument('--priority', type=str, help='Priority (0-7) for generation')
    parser.add_argument('--pgn', type=str, help='Parameter Group Number (decimal or hex) for generation')
    parser.add_argument('--source-address', type=str, help='Source Address (0-255) for generation')
    parser.add_argument('--reserved', type=str, default='0', help='Reserved bit (0 or 1, default: 0) for generation')
    
    args = parser.parse_args()
    
    if args.parse:
        # Parse mode
        try:
            can_id = int(args.parse, 0)  # Auto-detect base
            components = parse_j1939_id(can_id)
            
            print(f"\nParsed J1939 CAN ID 0x{can_id:08X} ({can_id}):")
            print(f"Priority:        {components['priority']} (0x{components['priority']:X})")
            print(f"Reserved:        {components['reserved']} (0x{components['reserved']:X})")
            print(f"Data Page:       {components['data_page']} (0x{components['data_page']:X})")
            print(f"PDU Format:      {components['pdu_format']} (0x{components['pdu_format']:02X})")
            print(f"PDU Specific:    {components['pdu_specific']} (0x{components['pdu_specific']:02X})")
            print(f"Source Address:  {components['source_address']} (0x{components['source_address']:02X})")
            print(f"PGN:             {components['pgn']} (0x{components['pgn']:04X})")
        except ValueError:
            print("Error: Invalid CAN ID format. Use decimal or hex (with 0x prefix).")
    
    elif args.generate:
        # Generate mode
        if not all([args.priority, args.pgn, args.source_address]):
            parser.error("--generate requires --priority, --pgn, and --source-address")
        
        try:
            priority = int(args.priority, 0)
            pgn = int(args.pgn, 0)
            source_address = int(args.source_address, 0)
            reserved = int(args.reserved, 0)
            
            can_id = build_j1939_id(priority, pgn, source_address, reserved)
            
            print(f"\nGenerated J1939 CAN ID:")
            print(f"Decimal: {can_id}")
            print(f"Hex:     0x{can_id:08X}")
            
            # Also show the components for verification
            components = parse_j1939_id(can_id)
            print("\nComponents (for verification):")
            print(f"Priority:        {components['priority']} (0x{components['priority']:X})")
            print(f"Reserved:        {components['reserved']} (0x{components['reserved']:X})")
            print(f"Data Page:       {components['data_page']} (0x{components['data_page']:X})")
            print(f"PDU Format:      {components['pdu_format']} (0x{components['pdu_format']:02X})")
            print(f"PDU Specific:    {components['pdu_specific']} (0x{components['pdu_specific']:02X})")
            print(f"Source Address:  {components['source_address']} (0x{components['source_address']:02X})")
            print(f"PGN:             {components['pgn']} (0x{components['pgn']:04X})")
        except ValueError as e:
            print(f"Error: Invalid input format - {e}")

if __name__ == '__main__':
    main()