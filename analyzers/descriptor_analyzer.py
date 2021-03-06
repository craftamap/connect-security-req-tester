import re
from distutils import util
from typing import List, Tuple

from models.descriptor_result import DescriptorResult
from models.requirements import Requirements, RequirementsResult
from reports.constants import (MISSING_ATTRS_SESSION_COOKIE,
                               MISSING_AUTHN_AUTHZ, MISSING_CACHE_HEADERS,
                               MISSING_REF_HEADERS, NO_ISSUES, REQ_TITLES)

REQ_CACHE_HEADERS = ['no-cache', 'no-store']
REF_DENYLIST = ['no-referrer-when-downgrade', 'unsafe-url']
COOKIE_PARSE = r'(.*); Domain=(.*); Secure=(.*); HttpOnly=(.*)'


class DescriptorAnalyzer(object):
    def __init__(self, desc_scan: DescriptorResult, requirements: Requirements):
        self.scan = desc_scan
        self.reqs = requirements

    def _check_cache_headers(self) -> Tuple[bool, List[str]]:
        passed = True
        proof: List[str] = []
        scan_res = self.scan.scan_results
        for link in scan_res:
            cache_headers = scan_res[link].cache_header.split(',')
            cache_headers = [x.strip().lower() for x in cache_headers]
            directives = all(item in cache_headers for item in REQ_CACHE_HEADERS)
            if not directives:
                proof.append(f"{link} | Cache header: {scan_res[link].cache_header}")
            passed = passed and directives

        return passed, proof

    def _check_referrer_headers(self) -> Tuple[bool, List[str]]:
        passed = True
        proof: List[str] = []
        scan_res = self.scan.scan_results
        for link in scan_res:
            ref_headers = scan_res[link].referrer_header.split(',')
            ref_headers = [x.strip().lower() for x in ref_headers]
            policy = ref_headers[0] not in REF_DENYLIST if ref_headers[0] != 'header missing' else False
            if not policy:
                proof.append(f"{link} | Referrer header: {scan_res[link].referrer_header}")
            passed = passed and policy

        return passed, proof

    def _check_cookie_headers(self) -> Tuple[bool, List[str]]:
        passed = True
        proof: List[str] = []
        scan_res = self.scan.scan_results
        scan_res = self.scan.scan_results
        for link in scan_res:
            cookies = scan_res[link].session_cookies
            for cookie in cookies:
                # Parsing the cookie string became messy, so we use a regex to match and tear
                # the string apart into its relevant pieces
                parsed = re.match(COOKIE_PARSE, cookie)
                secure = bool(util.strtobool(parsed.group(3)))
                httponly = bool(util.strtobool(parsed.group(4)))

                if not secure or not httponly:
                    proof.append(f"{link} | Cookie: {cookie}")
                passed = passed and secure and httponly

        return passed, proof

    def _check_authn_authz(self) -> Tuple[bool, List[str]]:
        passed = True
        proof: List[str] = []
        scan_res = self.scan.scan_results
        for link in scan_res:
            res_code = int(scan_res[link].res_code)
            auth_header = scan_res[link].auth_header
            req_method = scan_res[link].req_method
            if res_code >= 200 and res_code < 400:
                passed = False
                proof_text = f"{link} | Res Code: {res_code} Req Method: {req_method} Auth Header: {auth_header}"
                proof.append(proof_text)

        return passed, proof

    def analyze(self) -> Requirements:
        cache_passed, cache_proof = self._check_cache_headers()
        ref_passed, ref_proof = self._check_referrer_headers()
        cookies_passed, cookies_proof = self._check_cookie_headers()
        auth_passed, auth_proof = self._check_authn_authz()

        req2 = RequirementsResult(
            passed=cache_passed,
            description=[NO_ISSUES] if cache_passed else [MISSING_CACHE_HEADERS],
            proof=cache_proof,
            title=REQ_TITLES['2']
        )

        req5 = RequirementsResult(
            passed=auth_passed,
            description=[NO_ISSUES] if auth_passed else [MISSING_AUTHN_AUTHZ],
            proof=auth_proof,
            title=REQ_TITLES['5']
        )

        req11 = RequirementsResult(
            passed=cookies_passed,
            description=[NO_ISSUES] if cookies_passed else [MISSING_ATTRS_SESSION_COOKIE],
            proof=cookies_proof,
            title=REQ_TITLES['11']
        )

        req12 = RequirementsResult(
            passed=ref_passed,
            description=[NO_ISSUES] if ref_passed else [MISSING_REF_HEADERS],
            proof=ref_proof,
            title=REQ_TITLES['12']
        )

        self.reqs.req2 = req2
        self.reqs.req5 = req5
        self.reqs.req11 = req11
        self.reqs.req12 = req12

        return self.reqs
