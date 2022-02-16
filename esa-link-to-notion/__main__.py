import ast
from notion.block import (
    BasicBlock,
    PageBlock
)
from notion.client import NotionClient
import re
import settings
import sys

ESA_POST_PATTERN = r'https://[^\.]+\.esa\.io/posts/(\d+)'

def main():
    with open("mapping.txt") as f:
        lines = f.readlines()
    dict_str = "\n".join(lines)
    esa_notion_mapping = ast.literal_eval(dict_str)

    args = sys.argv
    parent_page_id = args[1]

    client = NotionClient(token_v2=settings.NOTION_TOKEN_V2)
    parent_page = client.get_block(parent_page_id)
    print(parent_page.children)

    for block in parent_page.children:
        change_url_recursively(block, esa_notion_mapping)

    # child_page_ids = []

    # for block in parent_page.children:
    #     if type(block) == PageBlock:
    #         child_page_ids.append(block.id)

    # print("処理する件数: %d" % len(child_page_ids))

    # for page_id in child_page_ids:
    #     page_id = page_id.replace("-", "")
    #     page = client.get_block(page_id)
    #     print("%s (%s)" % (page.title, page_id))

    #     children = page.children
    #     esa_id = int(children[0].title.replace("ID: ", ""))

    #     for block in children:
    #         change_url_recursively(block)

# block 内にさらに block がある場合も再帰的に ImageBlock を探し、Notion 向けに画像アップロードをおこなう
def change_url_recursively(block, esa_notion_mapping):
    if len(block.children) == 0:
        if isinstance(block, BasicBlock):
            pattern = re.compile(ESA_POST_PATTERN)
            title = block.title

            if pattern.search(title):
                def replace_method(matched):
                    esa_id = int(matched.group(1))
                    notion_id = esa_notion_mapping[esa_id]
                    return "https://www.notion.so/%s" % notion_id

                print(title)
                title = pattern.sub(replace_method, title)
                print(title)
                block.title = title
    else:
        for child_block in block.children:
            change_url_recursively(child_block, esa_notion_mapping)

main()
