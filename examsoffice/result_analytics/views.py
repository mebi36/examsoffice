import csv
from collections import defaultdict
import json

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.shortcuts import render
import pandas as pd

from result_analytics.models import AnalyticsData


# Create your views here.
def dashboard(request):
    template: str = "result_analytics/dashboard.html"
    return render(request, template, None)


def export_pivot_csv(request):
    analytics = AnalyticsData.objects.all()

    data = defaultdict(dict)
    result_names = []

    for a in analytics:
        result_names.append(a.name)
        for entry in a.results:
            reg_no = entry.get("reg_no")
            score = entry.get("score", "XX")
            score = score if not isinstance(score, str) else "XX"
            data[reg_no][a.name] = score

    result_names = sorted(result_names)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="collated_results.csv"'

    writer = csv.writer(response)
    writer.writerow(["Reg No"] + result_names)

    # Rows: student reg_no + scores
    for reg_no, results_dict in data.items():
        row = [reg_no]
        for rn in result_names:
            row.append(results_dict.get(rn, "XX"))
        writer.writerow(row)
    return response


def preview_excel(request):
    file = request.FILES["result_file"]
    try:
        df = pd.read_excel(file, header=None)
    except Exception as exc:
        return JsonResponse({"success": False, "error": str(exc)}, status=400)
    for col in df.columns:
        df_gen = df[df[col].str.contains(pat="[0-9]{4}/[0-9]{6}", regex=True, na=False)]

        if not df_gen.empty:
            break
    preview = df_gen.head(15).to_dict(orient="records")
    headers = list(df_gen.columns)
    return JsonResponse({
        "headers": headers,
        "preview": preview
    })


@require_http_methods({"POST"})
def upload_excel_file(request):
    if "result_file" not in request.FILES:
        return JsonResponse({"error": "No file uploaded"}, status=400)
    excel_file = request.FILES["result_file"]
    
    reg_no_col = int(request.POST.get("reg_col"))
    score_col = int(request.POST.get("score_col"))
    file_name = str(excel_file)

    try:
        df = pd.read_excel(excel_file, header=None)
    except Exception:
        return JsonResponse({"success": False, "error": "Error reading file."}, status=400)
    
    results_row_df = pd.DataFrame()
    try:
        if reg_no_col is None:
            # find reg number column
            for col in df.columns:
                df_gen = df[df[col].str.contains(pat="[0-9]{4}/[0-9]{6}", regex=True, na=False)]

                if not df_gen.empty:
                    print("col name: ", col)
                    print("all cols: ", df.columns)
                    print("col where found", df_gen)
                    reg_no_col = col
                    results_row_df = df_gen
                    break
            if reg_no_col is None:
                return JsonResponse({
                    "success": False,
                    "error": "Bad result formatting! Reg numbers not detected"
                }, status=400)
            results_row_df = results_row_df.iloc[:, reg_no_col:]

            results_row_df[reg_no_col] = results_row_df[reg_no_col].str.strip()
            try:
                results = results_row_df.copy()[[reg_no_col, 7]]
            except Exception:
                return JsonResponse({
                    "success": False, "error": "invalid template detected!"}, status=400)
            print(type(excel_file.__dict__))
            file_name = file_name[:7]
            results[99] = file_name
            results[reg_no_col] = results[reg_no_col].str.strip()
            results = results.rename(columns={reg_no_col: "reg_no", 7: "score", 99: "course"})
        else:
            results_row_df = df[df[reg_no_col].str.contains(pat="[0-9]{4}/[0-9]{6}", regex=True, na=False)]

            if score_col is not None:
                results = results_row_df.copy()[[reg_no_col, score_col]]
            else:
                return JsonResponse({
                    "success": False, "error": "score_col not specified"
                }, status=400)
            results[reg_no_col] = results[reg_no_col].str.strip()
            results = results.rename(columns={reg_no_col: "reg_no", score_col: "score"})
            results["course"] = file_name[:7]
    except Exception as exc:
        import traceback as tb
        print(tb.format_exc())
        return JsonResponse({"error": str(exc)}, status=500)
    return JsonResponse({"results": results.to_dict(orient="records")})


@csrf_exempt
@require_http_methods(["POST"])
def cache_result_data(request):
    try:
        data = json.loads(request.body)
        name = data.get("result_name")
        results = data.get("results", [])

        if AnalyticsData.objects.filter(name=name).exists():
            return JsonResponse({"error": "Result with this name already exists"}, status=400)
        
        AnalyticsData.objects.create(name=name, results=results)
        return JsonResponse({"message": "Result saved successfully"})
    except Exception as e:
        print(e)
        return JsonResponse({"error": str(e)}, status=500)


def list_results(request):
    saved = AnalyticsData.objects.values("id", "name", "created_at")
    return JsonResponse({"results": list(saved)})


def get_result(request, result_id):
    try:
        result = AnalyticsData.objects.get(id=result_id)
        return JsonResponse({"name": result.name, "results": result.results})
    except AnalyticsData.DoesNotExist:
        return JsonResponse({"error": "Result not found"}, status=400)


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_result(request, result_id):
    try:
        AnalyticsData.objects.get(id=result_id).delete()
    except Exception as exc:
        return JsonResponse({"success": False, "error": str(exc)}, status=500)
    else:
        return JsonResponse({"success": True})


@csrf_exempt
@require_http_methods(["DELETE"])
def clear_results(request):
    try:
        AnalyticsData.objects.all().delete()
        return JsonResponse({"message": "All results cleared"})
    except Exception as exc:
        return JsonResponse({"error": str(exc)}, status=500)
