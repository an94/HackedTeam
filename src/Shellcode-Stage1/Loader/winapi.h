#ifndef _WINAPI_H
#define _WINAPI_H

#include <windows.h>
#include <Wininet.h>
#include <ShlObj.h>

typedef HMODULE (WINAPI *LOADLIBRARYA)(__in LPSTR lpFileName);
typedef LOADLIBRARYA *PLOADLIBRARYA;
typedef HMODULE (WINAPI *LOADLIBRARYW)(__in LPWSTR lpFileName);
typedef LOADLIBRARYW *PLOADLIBRARYW;
typedef HMODULE (WINAPI *GETPROCADDRESS)(__in HMODULE hModule, __in LPSTR lpProcName);
typedef GETPROCADDRESS *PGETPROCADDRESS;

typedef LPVOID (WINAPI *VIRTUALALLOC)(__in LPVOID lpAddress, __in SIZE_T dwSize, __in DWORD flAllocationType, __in DWORD flProtect);
typedef BOOL (WINAPI *VIRTUALPROTECT)(__in LPVOID lpAddress, __in SIZE_T dwSize, __in DWORD flNewProtect, __out PDWORD lpflOldProtect);

typedef VOID (WINAPI *EXITPROCESS)(__in DWORD uExitReason);
typedef DWORD (WINAPI *GETSHORTPATHNAMEW)(__in LPWSTR lpszLongPath, __in LPWSTR lpszShortPath, __in DWORD cchBuffer);
typedef DWORD (WINAPI *GETMODULEFILENAMEW)(__in HMODULE hModule, __out LPWSTR lpFilename, __in DWORD nSize);
typedef BOOL (WINAPI *SHGETSPECIALFOLDERPATHW)(__in HWND hwndOwner, __out LPWSTR lpszPath, __in int csidl, __in BOOL fCreate);
typedef DWORD (WINAPI *GETFILEATTRIBUTESA)(__in LPSTR strFileName);
typedef BOOL (WINAPI *DELETEFILEA)(__in LPSTR lpFileName);
typedef HINTERNET (WINAPI *INTERNETOPENA)(__in LPSTR lpszAgent, __in DWORD dwAccessType, __in LPSTR lpszProxyName, __in LPSTR lpszProxyBypass, __in DWORD dwFlags);
typedef HINTERNET (WINAPI *INTERNETOPENURLA)(__in HINTERNET hInternet, __in LPSTR lpszUrl, __in LPSTR lpszHeaders,  __in DWORD dwHeadersLength, __in DWORD dwFlags, __in DWORD_PTR dwContext);
typedef BOOL (WINAPI *HTTPQUERYINFOW)(__in HINTERNET hRequest, __in DWORD dwInfoLevel, __inout LPVOID lpvBuffer, __inout LPDWORD lpdwBufferLength, __inout LPDWORD lpdwIndex);
typedef BOOL (WINAPI *INTERNETREADFILEEXA)(__in HINTERNET hFile, __in LPINTERNET_BUFFERS lpBuffersOut, __in DWORD dwFlags, __in DWORD dwContext);
typedef HANDLE (WINAPI *CREATEFILEW)(__in LPWSTR lpFileName, __in DWORD dwDesiredAccess, __in DWORD dwShareMode, __in LPSECURITY_ATTRIBUTES lpSecurityAttributes, __in DWORD dwCreationDisposition, __in DWORD dwFlagsAndAttributes, __in HANDLE hTemplateFile);
typedef BOOL (WINAPI *WRITEFILE)(__in HANDLE hFile, __in LPCVOID lpBuffer, __in DWORD nNumberOfBytesToWrite, __out LPDWORD lpNumberOfBytesWritten, __in LPOVERLAPPED lpOverlapped);
typedef UINT (WINAPIV *WTOI)(__in LPWSTR string);
typedef BOOL (WINAPI *GETUSERPROFILEDIRECTORYW)(__in HANDLE hToken, __out LPWSTR lpProfileDir, __in LPDWORD lpcchSize);
typedef BOOL (WINAPI *OPENPROCESSTOKEN)(__in HANDLE ProcessHandle, __in DWORD DesiredAccess, __out PHANDLE TokenHandle);
typedef BOOL (WINAPI *DELETEFILEA)(__in LPSTR strFileName);
typedef BOOL (WINAPI *FREELIBRARY)(__in HMODULE hMod);
typedef DWORD (WINAPI *WCSTOMBS)(__inout LPSTR lpStr, __in LPWSTR lpWstr, __in DWORD count);
typedef HANDLE (WINAPI *CREATETHREAD)(__in LPSECURITY_ATTRIBUTES lpThreadAttributes, __in SIZE_T dwStackSize, __in LPTHREAD_START_ROUTINE lpStartAddress, __in LPVOID lpParameter, __in DWORD dwCreationFlags, __out LPDWORD lpThreadId);
typedef DWORD (WINAPI *WAITFORSINGLEOBJECT)(__in HANDLE hHandle, __in DWORD dwMilliseconds);
typedef BOOL (WINAPI *TERMINATETHREAD)(__in HANDLE hThread, __in DWORD dwExitCode);
typedef BOOL (WINAPI *CLOSEHANDLE)(__in HANDLE hFile);
typedef BOOL (WINAPI *GETTEMPPATHW)(__in DWORD nBufferLength, __out LPWSTR lpBuffer);
typedef BOOL (WINAPI *SHGETKNOWNFOLDERPATH)(__in REFKNOWNFOLDERID rfid, __in DWORD dwFlags, __in HANDLE hToken, __out LPWSTR *ppszPath);
typedef BOOL (WINAPI *DELETEFILEW)(__in LPWSTR lpFileName);
#endif // _WINAPI_H