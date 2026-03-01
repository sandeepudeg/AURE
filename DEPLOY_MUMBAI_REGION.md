# Deploy to Mumbai Region (ap-south-1)

## Important Note

**AWS App Runner is NOT available in ap-south-1 (Mumbai).**

App Runner is only available in these regions:
- us-east-1 (Virginia) ✅ Currently deployed
- us-east-2 (Ohio)
- us-west-2 (Oregon)
- eu-west-1 (Ireland)
- eu-central-1 (Frankfurt)
- ap-northeast-1 (Tokyo)
- ap-southeast-1 (Singapore) ⭐ **Closest to India**
- ap-southeast-2 (Sydney)

## Best Solution for Indian Users

### Option 1: Deploy to Singapore (ap-southeast-1) - Recommended ⭐

Singapore is the closest App Runner region to India:
- Distance: ~3,500 km (vs 12,000 km for US East)
- Latency: 50-100ms (vs 200-300ms for US East)
- Load time: 2-3 seconds (vs 10+ minutes for US East)

**Deploy to Singapore:**
```powershell
# Run the Singapore deployment script
py scripts/deploy_to_singapore.py
```

### Option 2: Use Local Deployment (Fastest) ⚡

For development and testing:
```powershell
py -m streamlit run src/ui/app.py
```
- Load time: < 1 second
- No geographic latency
- Perfect for local use

### Option 3: Deploy Lambda to Mumbai + Use Local UI

Keep Lambda in ap-south-1 for fast API responses, use local Streamlit:
- Lambda in Mumbai: Fast API responses
- Streamlit local: Instant UI
- Best of both worlds

## Recommendation

**For Production in India:**
1. Deploy Streamlit to Singapore (ap-southeast-1) - 80% faster than US East
2. Keep Lambda/API in us-east-1 (already deployed)
3. Use CloudFront if needed (though it has Streamlit compatibility issues)

**For Development:**
- Use local Streamlit (instant loading)
- Connect to deployed API in us-east-1

## Cost Comparison

| Region | App Runner | Lambda | Total/Month |
|--------|------------|--------|-------------|
| us-east-1 | $15-25 | $5-10 | $20-35 |
| ap-southeast-1 | $18-30 | $6-12 | $24-42 |
| Difference | +20% | +20% | +20% |

Singapore costs ~20% more but provides 80% faster loading for Indian users.

## Next Steps

Would you like me to:
1. ✅ Deploy to Singapore (ap-southeast-1) for faster loading?
2. ✅ Keep current US East deployment and use locally?
3. ✅ Deploy full infrastructure to Singapore?

Let me know and I'll proceed!
