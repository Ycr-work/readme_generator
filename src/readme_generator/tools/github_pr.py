import json
import os
import requests
from github import Github,GithubException
from github.Repository import Repository
from github.Branch import Branch
from crewai import Agent,Task
from langchain.tool import tool
import traceback

GITHUB_API="https://api.github.com"

class GithubClient:
    def __init__(self,token:str,repo_name:str,base_branch:str="main"):
        self.client=Github(token)
        self.repo:Repository=self.client.get_repo(repo_name)
        self.base_branch=base_branch

    def get_or_create_branch(self,new_branch_name:str)->Branch:
        try:
            branch=self.repo.get_branch(new_branch_name)
            return branch
        except GithubException as e:
            source_branch=self.repo.get_branch(self.base_branch)
            self.repo.create_git_ref(ref=f"refs/heads/{new_branch_name}",sha=source_branch.commit.sha)
            return self.repo.get_branch(new_branch_name)
        
    def upsert_file(self,branch_name:str,file_path:str,content:str,commit_message:str):
        content_bytes=content.encode("utf-8")
        try:
            existing_file=self.repo.get_contents(file_path,ref=branch_name)
            if isinstance(existing_file,list):
                existing_file=existing_file[0]
            self.repo.update_file(
                path=file_path,
                message=commit_message,
                content=content_bytes,
                sha=existing_file.sha,
                branch=branch_name
            )
        except GithubException as e:
            if e.status==404:
                self.repo.create_file(
                    path=file_path,
                    messgae=commit_message,
                    content=content_bytes,
                    branch=branch_name
                )
            else:
                raise e
    
    def create_or_update_pr(self,branch_name:str,pr_titls:str,pr_body:str):
        open_pulls=self.repo.get_pulls(state="open",head=branch_name)
        if open_pulls.totalcount>0:
            pr=open_pulls[0]
            if pr.body!=pr_body:
                pr.edit(body=pr_body)
            return pr
    
    def run(self,text_content:str,branch_name:str,file_path:str="README.md"):
        self.get_or_create_branch(branch_name)

        commit_msg=f"docs:update {file_path} via automation"
        self.upsert_file(branch_name,file_path,text_content,commit_msg)

        pr_title=f"Update {file_path} from automation"
        pr_body=f"Automated update for `{file_path}`.\n\nGenerated content:\n```\n{text_content[:200]}...\n```"
        self.create_or_update_pr(branch_name, pr_title, pr_body)


class GithubPRTool():
    
    @tool("根据PR所需的相关参数,上传对应repo的branch的pr")
    def github_pr(github_token:str,repo:str,base_branch:str,head_branch:str,edited_content:str):
        try:
            client=GithubClient(github_token=github_token,repo_name=repo,base_branch=base_branch)
            client.run(text_content=edited_content,branch_name=head_branch)
        except Exception as e:
            traceback.print_exc()
            raise e
        
    @tool("根据PR所需的相关参数,验证对应repo的branch的pr是否存在")
    def validate_pr(github_token:str,repo:str,base_branch:str,head_branch:str):
        pass

    @tool("根据PR所需的相关参数，创建新的对应repo的branch的pr")
    def create_pr(github_token:str,repo:str,base_branch:str,head_branch):
        pass
    
