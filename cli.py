import argparse
from campaign_manager import CampaignManager, delete_campaign, list_campaigns


def main():
    parser = argparse.ArgumentParser(description="Manage campaigns")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("list")

    create_p = sub.add_parser("create")
    create_p.add_argument("name")

    del_p = sub.add_parser("delete")
    del_p.add_argument("name")

    args = parser.parse_args()
    if args.cmd == "list":
        for name in list_campaigns():
            print(name)
    elif args.cmd == "create":
        CampaignManager(args.name)
        print(f"Created campaign {args.name}")
    elif args.cmd == "delete":
        if delete_campaign(args.name):
            print(f"Deleted campaign {args.name}")
        else:
            print("Campaign not found")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
